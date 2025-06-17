import pytest
import requests
import json
from test_config import BASE_URL

SESSION_ID = "6499499654562971648"

def test_initialize_session():
    """Test initializing a session with the agent"""
    uid = "test_user_001"
    session_id = SESSION_ID
    
    url = f"{BASE_URL}/apps/se/initialize_session/{uid}/{session_id}"
    
    try:
        response = requests.post(url)
        print("\nInitialize Session Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == "success"
        assert "message" in response_data
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {str(e)}")
    except ValueError as e:
        pytest.fail(f"Failed to parse response: {str(e)}")

def test_run_agent():
    """Test running the agent with a question"""
    uid = "test_user_001"
    session_id = SESSION_ID
    question = "I feel panic. How can you help me?"
    
    url = f"{BASE_URL}/apps/se/run_agent/{uid}/{session_id}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "question": question
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("\nRun Agent Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == "success"
        assert "agent_response" in response_data
        assert isinstance(response_data["agent_response"], list)
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {str(e)}")
    except ValueError as e:
        pytest.fail(f"Failed to parse response: {str(e)}")

