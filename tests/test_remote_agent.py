import pytest
import requests
import time
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request

LOCATION="us-central1"
PROJECT_ID="gcpxmlb25"
AGENT_ENGINE_ID="638851440109944832"
SERVICE_ACCOUNT_FILE = "gcpxmlb25-e063bdf91528.json"

# SESSION_ID = "2805844272677388288"
SESSION_ID = "7884778752444465152"
SESSION_ID_Delete = "8434851225681264640"

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
    create_session_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions"
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

        operation_status_url = f"https://us-central1-aiplatform.googleapis.com/v1beta1/{operation_name}" # Use the full API path for polling
        # You might need to adjust this base URL if your API is not us-central1 specific for operations
        # A more robust way might be: f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/{operation_name}"

        max_retries = 10
        for i in range(max_retries):
            time.sleep(2) # Wait for 2 seconds before polling
            print(f"Polling operation (attempt {i+1}/{max_retries})...")
            # **THE FIX IS HERE: Pass headers to the GET request**
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

    # 1. Create a dynamic session first
    try:
        current_session_id = test_create_a_session_v2()
    except Exception as e:
        pytest.fail(f"Failed to create session: {e}")

    """Test sending a query to the agent"""
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions/{current_session_id}:query"
    # url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions/{SESSION_ID}:run"
    
    # Get authentication token
    token = get_google_auth_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # # Prepare the request payload
    # payload = {
    #     "content": {
    #         "role": "user",
    #         "parts": [
    #             { "text": "I feel panic.  How can you help me?" }
    #         ]
    #     }
    # }

    payload = {
    "input": {
    "question": "I feel panic.  How can you help me?",
    "userId": "test_user_001",
    # Use the dynamically obtained current_session_id here too
    "session_id": f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}/sessions/{current_session_id}"
    # "session_id": SESSION_ID
    },
    "method": "query"
    }


    
    print("\nMaking API request to:", url)
    print("Request payload:", payload)
    print("Headers:", {k: v[:20] + '...' if k == 'Authorization' else v for k, v in headers.items()})
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("\nSend Query Response:")
        print(response)
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

        
