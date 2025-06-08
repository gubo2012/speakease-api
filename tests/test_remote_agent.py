import pytest
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

LOCATION="us-central1"
PROJECT_ID="gcpxmlb25"
AGENT_ENGINE_ID=""
SERVICE_ACCOUNT_FILE = "gcpxmlb25-e063bdf91528.json"

SESSION_ID = "s_234"

def get_google_auth_token():
    """Get OAuth2 token using service account credentials"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        print("\nAuthentication successful!")
        print(f"Service Account Email: {credentials.service_account_email}")
        print(f"Token State: {credentials.token_state}")
        # print(f"Access Token: {credentials.token[:20]}...")  # Print first 20 chars of token
        # print(f"Access Token: {credentials.token}")  # Print first 20 chars of token
        return credentials.token
    except Exception as e:
        print(f"\nAuthentication Error: {str(e)}")
        raise


def test_get_sessions():
    """Test getting sessions from Google Cloud AI Platform"""
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions"
    
    # Get authentication token
    token = get_google_auth_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\nMaking API request to:", url)
    response = requests.get(url, headers=headers)
    print("\nGet Sessions Response:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

        
