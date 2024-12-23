import requests
import streamlit as st
from msal import ConfidentialClientApplication
import os
from dotenv import load_dotenv

# Load environment variables from a `.env` file
load_dotenv()

# Configuration variables (consider using a dedicated config file)
CLIENT_ID = os.environ.get('CLIENT_ID')
TENANT_ID = os.environ.get('TENANT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI')
SCOPES = ["User.Read"]  # Define required scopes here

def initialize_app():
    """Initializes the ConfidentialClientApplication object."""
    authority_url = f"https://login.microsoftonline.com/{TENANT_ID}"
    try:
        return ConfidentialClientApplication(
            client_id=CLIENT_ID,
            authority=authority_url,
            client_credential=CLIENT_SECRET,
        )
    except Exception as e:
        st.error("An error occurred while initializing the application. Please try again later.")
        return None  # Indicate failure

def acquire_access_token(app, code):
    """Acquires an access token using the authorization code."""
    try:
        token_result = app.acquire_token_by_authorization_code(code, scopes=SCOPES, redirect_uri=REDIRECT_URI)
        if "access_token" in token_result:
            return token_result
        else:
            st.error("Failed to acquire access token. Please check your input and try again.")
            return None
    except Exception as e:
        st.error("An error occurred while acquiring the access token. Please try again later.")
        return None

def fetch_user_data(access_token):
    """Fetches user data from the Microsoft Graph API."""
    headers = {"Authorization": f"Bearer {access_token}"}
    graph_api_endpoint = "https://graph.microsoft.com/v1.0/me"
    response = requests.get(graph_api_endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("An error occurred while fetching user data. Please try again later.")
        return None

def authentication_process(app):
    """Handles the authentication flow with Streamlit."""
    auth_url = app.get_authorization_request_url(scopes=SCOPES, redirect_uri=REDIRECT_URI)
    st.sidebar.markdown(f"Please go to [this URL]({auth_url}) and authorize the app.")

    if st.query_params.get("code"):
        access_token = acquire_access_token(app, st.query_params.get("code"))
        if access_token:
            user_data = fetch_user_data(access_token["access_token"])
            if user_data:
                st.session_state["user_id"] = user_data.get("id")  # Assuming user ID is in "id" field
                st.session_state["token"] = access_token
                return user_data, access_token
            else:
                st.error("Failed to fetch user data")
        # Handle potential errors during token acquisition or user data retrieval

def get_user_id():
    """Retrieves the user ID from session state, if available."""
    return st.session_state.get("user_id")

def get_token():
    """Retrieves the access token from session state, if available."""
    return st.session_state.get("token")