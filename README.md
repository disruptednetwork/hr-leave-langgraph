# HR Leave Chatbot Application

## Overview

The HR Leave Checking Application is a Streamlit-based chatbot app designed to simplify employee interactions regarding leave balance and leave requests. It integrates with Google Vertex AI and uses LangChain/LangGraph to handle user queries through a workflow. The app also includes a secure login process using Azure AD authentication

See more details in the blogs written in Thai language:

- [HR APP with Streamlit + Cloud Run + Gemini + Cloud SQL with authentication through Azure AD](https://medium.com/google-cloud-thailand/hr-app-%E0%B9%80%E0%B8%8A%E0%B9%87%E0%B8%84%E0%B8%A7%E0%B8%B1%E0%B8%99%E0%B8%A5%E0%B8%B2%E0%B9%81%E0%B8%9A%E0%B8%9A%E0%B8%A5%E0%B8%B9%E0%B8%81%E0%B8%97%E0%B8%B8%E0%B9%88%E0%B8%87%E0%B8%88%E0%B8%B2%E0%B8%99%E0%B8%94%E0%B9%88%E0%B8%A7%E0%B8%99-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-streamlit-cloud-run-gemini-cloud-sql-%E0%B9%81%E0%B8%A5%E0%B8%B0%E0%B8%97%E0%B8%B3)
- [HR APP part 2 with LangChain](https://medium.com/@disruptednetwork/hr-app-%E0%B9%80%E0%B8%8A%E0%B9%87%E0%B8%84%E0%B8%A7%E0%B8%B1%E0%B8%99%E0%B8%A5%E0%B8%B2%E0%B9%81%E0%B8%9A%E0%B8%9A%E0%B8%A5%E0%B8%B9%E0%B8%81%E0%B8%97%E0%B8%B8%E0%B9%88%E0%B8%87%E0%B8%88%E0%B8%B2%E0%B8%99%E0%B8%94%E0%B9%88%E0%B8%A7%E0%B8%99%E0%B8%A0%E0%B8%B2%E0%B8%84-2-langchain-3f800cfc2ab0)
- [HR APP part 3 with LangGraph](https://medium.com/google-cloud-thailand/hr-app-เช็ควันลาแบบลูกทุ่งจานด่วนภาค-3-langgraph-6d82aae163a6)
- [HR APP final with leave request](https://medium.com/@disruptednetwork/hr-app-%E0%B9%80%E0%B8%8A%E0%B9%87%E0%B8%84%E0%B8%A7%E0%B8%B1%E0%B8%99%E0%B8%A5%E0%B8%B2%E0%B9%81%E0%B8%9A%E0%B8%9A%E0%B8%A5%E0%B8%B9%E0%B8%81%E0%B8%97%E0%B8%B8%E0%B9%88%E0%B8%87%E0%B8%88%E0%B8%B2%E0%B8%99%E0%B8%94%E0%B9%88%E0%B8%A7%E0%B8%99%E0%B8%A0%E0%B8%B2%E0%B8%84%E0%B8%88%E0%B8%9A-gemini-langgraph-cloudsql-cloud-run-streamlit-ac4a6eb914d3)

## Features

- **Leave Balance Inquiry**: Retrieve detailed leave balance information for the authenticated user.
- **LangGraph Integration**: Sophisticated state management and AI-driven workflows using LangGraph.
- **Secure Authentication**: Login process integrated with Azure Active Directory.
- **Chat Interface**: User-friendly chat interface for seamless interaction.
- **Google Vertex AI Integration**: Uses Vertex AI for language model functionality.
- **Cloud Run Deployment**: Easily deployable to Google Cloud Run.

## Technologies Used

- **Streamlit**: For the app's user interface.
- **Google Vertex AI**: To handle natural language processing and response generation.
- **LangChain**: For tool orchestration and intent handling.
- **LangGraph**: For state management and enhanced conversational workflows.
- **Azure Active Directory**: For secure user authentication.
- **Python**: Core programming language for the application.
- **PostgreSQL**: For database management.
- **Google Cloud Run**: For serverless deployment.
- **LangFuse**: For monitoring and debugging AI workflows.

## Setup Instructions

### Prerequisites

1. Python 3.8 or higher installed.
2. Access to a Google Cloud Project with Vertex AI and Cloud Run enabled.
3. Azure Active Directory app registration for authentication.
4. PostgreSQL database setup for storing user leave balance information.

### Environment Variables

Set the following environment variables in your system:

- `PROJECT_ID`: Your Google Cloud Project ID.
- `REGION`: The region for Vertex AI.
- `MODEL_NAME`: The name of your Vertex AI model.
- `POSTGRES_HOST`: Hostname or IP address of your PostgreSQL database.
- `POSTGRES_DB`: Name of the PostgreSQL database.
- `POSTGRES_USER`: Username for the PostgreSQL database.
- `POSTGRES_PASSWORD`: Password for the PostgreSQL database.
- `CLIENT_ID`: Azure AD client ID.
- `TENANT_ID`: Azure AD tenant ID.
- `CLIENT_SECRET`: Azure AD client secret (stored in Secret Manager).
- `REDIRECT_URI`: Redirect URI for Azure AD authentication.
- `LANGFUSE_SECRET_KEY`: Secret key for LangFuse integration.
- `LANGFUSE_PUBLIC_KEY`: Public key for LangFuse integration.
- `LANGFUSE_HOST`: Host URL for LangFuse integration.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/disruptednetwork/hr-leave-langgraph.git
   cd hr-leave-langgraph
   ```

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application locally:

   ```bash
   streamlit run main.py
   ```

### Deploying to Google Cloud Run

The service can be deployed on Google Cloud Run. Detailed deployment steps and configurations are outlined in this [blog](https://medium.com/google-cloud-thailand/hr-app-เช็ควันลาแบบลูกทุ่งจานด่วนโดยใช้-streamlit-ผ่าน-cloud-run-gemini-cloud-sql-และทำ-2fbce13ab119).

## Usage

1. Navigate to the app in your browser using the Cloud Run URL.
2. Log in using your Azure AD credentials via the sidebar.
3. Use the chat interface to:
   - Query leave balances by asking questions like "What is my leave balance?"

## Code Structure

- **main.py**: Entry point for the Streamlit application.
- **app/auth.py**: Handles Azure AD authentication processes.
- **app/db.py**: Database connection and query utilities.

## Tools Defined

1. **fetch\_leave\_balance**: Fetches the user's leave balance from the database.
2. **request\_leave**: Submit a leave request for the user.
3. **fetch\_pending\_requests**: Fetches all pending leave requests for the user.

## Workflow Enhancements

- **LangGraph Workflow**: Utilizes LangGraph to manage state transitions and AI-driven workflows.
- **Fallback Mechanisms**: Ensures robustness by handling tool errors gracefully.
- **Memory Saver**: Utilizes LangGraph’s memory saver for efficient state management.

## Acknowledgments

#### The Azure AD authentication was inspired by and incorporates ideas from:
- [Streamlit login with Azure AD Authentication](https://medium.com/@prhmma/streamlit-login-with-azure-ad-authentication-66ebd1691858)
- [GitHub Repository: Streamlit Authentication with Azure AD](https://github.com/Prhmma/Streamlit_Azure_AD)

#### LangGraph implementation was inspired by and incorporates ideas from:
- [Customer support bot tutorial](https://langchain-ai.github.io/langgraph/tutorials/customer-support/customer-support/)
- [Introduction to AI Agent with LangChain and LangGraph: A Beginner’s Guide](https://medium.com/@cplog/building-tool-calling-conversational-ai-with-langchain-and-langgraph-a-beginners-guide-8d6986cc589e)
