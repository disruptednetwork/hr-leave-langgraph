import streamlit as st
from datetime import datetime
from app.auth import initialize_app, authentication_process
from app import db
import vertexai
import dotenv
import os
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_vertexai import ChatVertexAI
from langfuse.callback import CallbackHandler

dotenv.load_dotenv()

langfuse_handler = CallbackHandler(
  secret_key=os.environ.get('LANGFUSE_SECRET_KEY'),
  public_key=os.environ.get('LANGFUSE_PUBLIC_KEY'),
  host=os.environ.get('LANGFUSE_HOST')
)

# Environment variable setup for Vertex AI
PROJECT_ID = os.environ.get('PROJECT_ID')
REGION = os.environ.get('REGION')
MODEL_NAME = os.environ.get('MODEL_NAME')

# Initialize VertexAI
vertexai.init(project=PROJECT_ID, location=REGION)  

# Set up LLM
chat_llm = ChatVertexAI(
    model_name=MODEL_NAME,
    max_output_tokens=8192,
    temperature=1.0,
    top_p=0.95
)

# Define State
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistant:
    """Encapsulates the assistant logic for handling runnable tasks."""
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            user_id = configuration.get("user_id", None)
            state = {**state, "user_info": user_id}
            result = self.runnable.invoke(state)
            
            # Re-prompt if LLM returns an empty response
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
      
@tool
def fetch_leave_balance(user_id: str):
    """Fetches the user's leave balance from the database."""
    conn = db.connect_to_db()
    if conn:
        try:
            #user_id = get_user_id()
            if user_id:
                leave_balance = db.fetch_user_leave_balance(conn, user_id)
                if leave_balance:
                    response = "Your leave balance:\n\n"
                    for leave_type, available, used in leave_balance:
                        response += f"- {leave_type}: Available: {available}, Used: {used}\n"
                    return response
                return f"No leave balance found for your account."
            return f"User ID not found. Please log in again."
        except Exception as e:
            return f"Error fetching leave balance: {e}"
        finally:
            conn.close()
    return f"Failed to connect to the database."

# Tools to use
tools_to_use = [fetch_leave_balance]

# Prompts
primary_assistant_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the provided tools to assist with tasks such as fetching leave balance."
              "\n\nCurrent user:\n\n{user_info}\n"
              "\nCurrent time: {time}."),
    ("placeholder", "{messages}"),
]).partial(time=datetime.now())

# Runnables
assistant_runnable = primary_assistant_prompt | chat_llm.bind_tools(tools_to_use)


# Helper functions
def handle_tool_error(error):
    return f"An error occurred while using the tool: {str(error)}"

def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

# Graph construction
def build_graph() -> StateGraph:
    builder = StateGraph(State)
    builder.add_node("assistant", Assistant(assistant_runnable))
    builder.add_node("tools", create_tool_node_with_fallback(tools_to_use))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder

# Streamlit Application
def main():
    """
    Main function for the HR Leave Application Streamlit app.
    """

    # Set up the page configuration
    st.set_page_config(page_title="HR Leave App", page_icon=":date:")

    # Sidebar for user authentication
    st.sidebar.title("Login")

    # Ensure session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Authentication process
    if not st.session_state["authenticated"]:
        app = initialize_app()
        if app is not None:
            auth_result = authentication_process(app)
            if auth_result:
                user_data, token = auth_result
                st.session_state["authenticated"] = True
                st.session_state["display_name"] = user_data.get("displayName")
                st.session_state["user_id"] = user_data.get("id")
                st.session_state["token"] = token
                st.rerun()
        return
    
    # Chat Interface
    st.title("HR Leave Chatbot")
    st.sidebar.write(f"Welcome, {st.session_state['display_name']}")
    
    # Initialize message history
    if "messages" not in st.session_state:
        st.session_state["messages"] = [AIMessage(content="How can I help you with your leave today?")]

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message("assistant" if isinstance(message, AIMessage) else "user"):
            st.markdown(message.content)

    # User Input
    if prompt := st.chat_input("Enter your query"):
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Run LangGraph Workflow
        builder = build_graph()
        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)
        import uuid
        thread_id = str(uuid.uuid4())

        config = {
            "configurable": {
                # fetch the user's id
                "user_id": st.session_state["user_id"],
                # Checkpoints are accessed by thread_id
                "thread_id": thread_id,
            },
            "callbacks": [langfuse_handler]
        }
        _printed = set()
        final_ai_message = None
        tool_message = None
        events = graph.stream(
            {"messages": ("user", prompt)},
            config,
            stream_mode="values"
        )
        
        for event in events:
            # Extract AI response and append it to session state
            message = event.get("messages")
            if message:
                if isinstance(message, list):
                    message = message[-1]
                if isinstance(message, ToolMessage):
                    tool_message = message
                # Check if the message is the final AI response
                elif isinstance(message, AIMessage):
                    final_ai_message = message
                    _printed.add(message.id)
        # Display the tool response in an expander
        if tool_message:
            with st.chat_message("assistant"):
                with st.expander(f"Tool Call: {tool_message.name}"):
                    st.markdown(f"**Tool Name:** {tool_message.name}")
                    st.markdown(f"**Tool Output:**\n\n{tool_message.content}")

        # Display the final AI response
        if final_ai_message:
            st.session_state["messages"].append(final_ai_message)
            with st.chat_message("assistant"):
                st.markdown(final_ai_message.content)



# Entry point for the application
if __name__ == "__main__":
    main()