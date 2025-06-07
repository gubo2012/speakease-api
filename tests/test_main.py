import pytest
import requests
from test_config import BASE_URL, TEST_USER_UID

def test_outgoing_paraphrase_success():
    """Test successful outgoing paraphrase request"""
    response = requests.post(
        f"{BASE_URL}/apps/se/outgoing_paraphrase",
        json={"text_content": "I like trains. Trains are fun. I like trains."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "paraphrase" in data
    assert isinstance(data["paraphrase"], str)
    assert len(data["paraphrase"]) > 0
    print("\nOutgoing Paraphrase Result:")
    print(f"Input: I like trains. Trains are fun. I like trains.")
    print(f"Output: {data['paraphrase']}")

def test_incoming_paraphrase_success():
    """Test successful incoming paraphrase request"""
    response = requests.post(
        f"{BASE_URL}/apps/se/incoming_paraphrase",
        json={"text_content": "It's raining cats and dogs!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "paraphrase" in data
    assert isinstance(data["paraphrase"], str)
    assert len(data["paraphrase"]) > 0
    print("\nIncoming Paraphrase Result:")
    print(f"Input: It's raining cats and dogs!")
    print(f"Output: {data['paraphrase']}")