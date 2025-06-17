import pytest
import requests
import time
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import json

LOCATION="us-central1"
PROJECT_ID="gcpxmlb25"
# PROJECT_ID = "842207255412"
AGENT_ENGINE_ID="638851440109944832"
SERVICE_ACCOUNT_FILE = "gcpxmlb25-e063bdf91528.json"

# SESSION_ID = "2805844272677388288"
SESSION_ID = "6499499654562971648"
SESSION_ID_Delete = "6917349257489940480"

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

# This function needs to be implemented as discussed previously, including polling
def test_create_a_session_v2():
    """Creates a session, polls for completion, and returns its ID."""
    token = get_google_auth_token()
    print(f"Auth token: {token}")
    # create_session_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions"
    create_session_url = f"https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'userId': 'test_user_001' # Adjust payload as needed for session creation
    }

    print("\nMaking POST request to:", create_session_url)
    print("Request payload:", payload)

    try:
        response = requests.post(create_session_url, headers=headers, json=payload)
        response.raise_for_status()

        create_session_response_json = response.json()
        print("\nCreate Session Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        operation_name = create_session_response_json.get('name')
        if not operation_name:
            raise ValueError("Operation name not found in create session response.")

        print(f"\nCreated operation: {operation_name}. Polling for completion...")

        # Use the same project ID and location as the create session request
        # operation_status_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/operations/{operation_name.split('/')[-1]}"
        # operation_status_url = f"https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/operations/{operation_name.split('/')[-1]}"
        operation_status_url = f"https://aiplatform.googleapis.com/v1beta1/{operation_name}"
# Or, if you want to be explicit with the base URL:

        max_retries = 10
        for i in range(max_retries):
            time.sleep(2) # Wait for 2 seconds before polling
            print(f"Polling operation (attempt {i+1}/{max_retries})...")
            # **THE FIX IS HERE: Pass headers to the GET request**
            print(f"Polling URL: {operation_status_url}") # Add this
            print(f"Headers for polling: {headers}") # Add this
            op_response = requests.get(operation_status_url, headers=headers)
            op_response.raise_for_status()
            op_json = op_response.json()

            if op_json.get('done'):
                print("Operation is done!")
                # Extract the session name from the 'response' field of the operation
                session_full_name = op_json.get('response', {}).get('name')
                if session_full_name:
                    session_id = session_full_name.split('/')[-1]
                    print(f"New session created with ID: {session_id}")
                    return session_id
                else:
                    raise ValueError("Session name not found in completed operation response.")
            elif op_json.get('error'):
                error_details = op_json['error']
                raise RuntimeError(f"Operation failed: {error_details}")

        raise TimeoutError("Session creation operation timed out.")

    except requests.exceptions.RequestException as e:
        error_details = f"Error during session creation: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_details += f"\nResponse: {e.response.text}"
        print(error_details)
        raise
    except Exception as e:
        print(f"An unexpected error occurred during session creation: {e}")
        raise


def test_list_sessions():
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

def test_get_a_session():
    """Test getting a specific session from Google Cloud AI Platform"""
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions/{SESSION_ID}"
    
    # Get authentication token
    token = get_google_auth_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\nMaking API request to:", url)
    response = requests.get(url, headers=headers)
    print("\nGet Session Response:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_send_query():
    """Test sending a streaming query to the agent"""
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}:streamQuery?alt=sse"
    
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
            "message": "I feel panic. How can you help me?",
            "user_id": "test_user_001",
        }
    }
    
    print("\nMaking API request to:", url)
    print("Request payload:", payload)
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        print("\nSend Query Response:")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"\nError: Request failed with status code {response.status_code}")
            if response.text:
                print(f"Error details: {response.text}")
            assert False, f"Request failed with status code {response.status_code}"
        
        # Process the streaming response
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
                                    text_part = part["text"]
                                    print(f"Response: {text_part}")
                except json.JSONDecodeError:
                    print(f"Raw line: {line_text}")
        
        assert response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed with error: {str(e)}")
        raise
    except ValueError as e:
        print(f"\nFailed to parse JSON response: {str(e)}")
        print(f"Raw response content: {response.text}")
        raise

def test_delete_a_session():
    """Test deleting a specific session from Google Cloud AI Platform"""
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions/{SESSION_ID_Delete}"
    
    # Get authentication token
    token = get_google_auth_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\nMaking DELETE request to:", url)
    response = requests.delete(url, headers=headers)
    print("\nDelete Session Response:")
    print(f"Status Code: {response.status_code}")
    print(response)
    if response.text:
        print(f"Response: {response.text}")
    assert response.status_code == 200

def test_create_a_session():
    """Test creating a new session in Google Cloud AI Platform"""
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions"
    
    # Get authentication token
    token = get_google_auth_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Prepare the request payload
    payload = {
        "userId": "test_user_001"  # You can modify this or make it a constant
    }
    
    print("\nMaking POST request to:", url)
    print("Request payload:", payload)
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("\nCreate Session Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text}")
        
        if response.status_code != 200:
            print(f"\nError: Request failed with status code {response.status_code}")
            if response.text:
                print(f"Error details: {response.text}")
            assert False, f"Request failed with status code {response.status_code}"
            
        response_json = response.json()
        print(f"Response JSON: {response_json}")
        assert response.status_code == 200
        
        # Store the new session ID if needed
        if 'name' in response_json:
            session_id = response_json['name'].split('/')[-1]
            print(f"\nNew session created with ID: {session_id}")
            
    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed with error: {str(e)}")
        raise
    except ValueError as e:
        print(f"\nFailed to parse JSON response: {str(e)}")
        print(f"Raw response content: {response.text}")
        raise

        
