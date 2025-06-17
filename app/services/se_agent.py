import requests
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from app.config.cloud_config import GCP_PROJECT_ID

LOCATION = "us-central1"
AGENT_ENGINE_ID = "638851440109944832"
SERVICE_ACCOUNT_FILE = "gcpxmlb25-e063bdf91528.json"

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
        return credentials.token
    except Exception as e:
        print(f"\nAuthentication Error: {str(e)}")
        raise

def initialize_session(uid: str, session_id: str) -> str:
    """Initialize a session with the agent server."""
    url = f"https://aiplatform.googleapis.com/v1beta1/projects/{GCP_PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions"
    
    # Get authentication token
    token = get_google_auth_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Prepare the request payload
    payload = {
        "userId": uid
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        response_json = response.json()
        if 'name' in response_json:
            session_id = response_json['name'].split('/')[-1]
            print(f"\nNew session created with ID: {session_id}")
            return session_id
        else:
            raise ValueError("Session ID not found in response")
            
    except requests.exceptions.RequestException as e:
        print(f"Error initializing session: {e}")
        raise
    except ValueError as e:
        print(f"Failed to parse response: {e}")
        raise

def extract_texts(obj):
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'text':
                results.append(v)
            else:
                results.extend(extract_texts(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(extract_texts(item))
    return results

def run_agent(question: str, uid: str, session_id: str) -> list:
    """Send a question to the agent server using the streaming query endpoint.
    Args:
        question (str): The question to ask the agent
        uid (str): The user id
        session_id (str): The session id
    Returns:
        list: List of text responses from the agent
    """
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{GCP_PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}:streamQuery?alt=sse"
    
    # Get authentication token
    token = get_google_auth_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Prepare the request payload
    payload = {
        "class_method": "stream_query",
        "input": {
            "message": question,
            "user_id": uid,
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        
        texts = []
        for line in response.iter_lines():
            if line:
                # Decode the line and remove the "data: " prefix if present
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    line_text = line_text[6:]  # Remove "data: " prefix
                try:
                    event = json.loads(line_text)
                    if "content" in event:
                        if "parts" in event["content"]:
                            parts = event["content"]["parts"]
                            for part in parts:
                                if "text" in part:
                                    texts.append(part["text"])
                except json.JSONDecodeError:
                    print(f"Raw line: {line_text}")
        
        return texts
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with the agent server: {e}")
        raise
    except ValueError as e:
        print(f"Failed to parse response: {e}")
        raise
