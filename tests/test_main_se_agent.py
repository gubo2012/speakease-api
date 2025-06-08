import pytest
import httpx

BASE_URL = "http://localhost:8000"
UID = "u_234"
SESSION_ID = "s_234"

def test_initialize_session():
    with httpx.Client(base_url=BASE_URL) as client:
        response = client.post(f"/apps/se/initialize_session/{UID}/{SESSION_ID}")
        print("Initialize session response:", response.json())
        assert response.status_code == 200

def test_run_agent():
    with httpx.Client(base_url=BASE_URL, timeout=15) as client:
        payload = {"question": "I feel panic, what should I do? Suggest something, e.g., a breathing exercise"}
        response = client.post(f"/apps/se/run_agent/{UID}/{SESSION_ID}", json=payload)
        print("Run agent response:", response.json())
        assert response.status_code == 200

def test_run_agent2():
    with httpx.Client(base_url=BASE_URL, timeout=15) as client:
        payload = {"question": "Yes, send to the root agent, what should I do"}
        response = client.post(f"/apps/se/run_agent/{UID}/{SESSION_ID}", json=payload)
        print("Run agent response:", response.json())
        assert response.status_code == 200