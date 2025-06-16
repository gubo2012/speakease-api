import pytest
import requests
from test_config import BASE_URL, TEST_USER_UID
from datetime import datetime

# Test user data
TEST_USER_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "grade_level": 8,
    "group_ids": ["group1", "group2"],
    "language": "en",
    "preferred_type": "text"
}

def test_create_user():
    """Test creating a new user"""
    url = f"{BASE_URL}/apps/se/users/{TEST_USER_UID}"
    print('url: ', url)
    
    response = requests.post(url, json=TEST_USER_DATA)
    print(response)
    assert response.status_code == 200
    
    user_data = response.json()
    assert user_data["first_name"] == TEST_USER_DATA["first_name"]
    assert user_data["last_name"] == TEST_USER_DATA["last_name"]
    assert user_data["grade_level"] == TEST_USER_DATA["grade_level"]
    assert user_data["group_ids"] == TEST_USER_DATA["group_ids"]
    assert user_data["language"] == TEST_USER_DATA["language"]
    assert user_data["preferred_type"] == TEST_USER_DATA["preferred_type"]
    assert "created_at" in user_data

def test_create_duplicate_user():
    """Test creating a user that already exists"""
    url = f"{BASE_URL}/apps/se/users/{TEST_USER_UID}"
    
    response = requests.post(url, json=TEST_USER_DATA)
    assert response.status_code == 409  # Conflict

def test_get_user():
    """Test retrieving user information"""
    url = f"{BASE_URL}/apps/se/users/{TEST_USER_UID}"
    
    response = requests.get(url)
    assert response.status_code == 200
    
    user_data = response.json()
    assert user_data["first_name"] == TEST_USER_DATA["first_name"]
    assert user_data["last_name"] == TEST_USER_DATA["last_name"]
    assert user_data["grade_level"] == TEST_USER_DATA["grade_level"]
    assert user_data["group_ids"] == TEST_USER_DATA["group_ids"]
    assert user_data["language"] == TEST_USER_DATA["language"]
    assert user_data["preferred_type"] == TEST_USER_DATA["preferred_type"]

def test_get_nonexistent_user():
    """Test retrieving a user that doesn't exist"""
    url = f"{BASE_URL}/apps/se/users/nonexistent_user"
    
    response = requests.get(url)
    assert response.status_code == 404

def test_update_user():
    """Test updating user information"""
    url = f"{BASE_URL}/apps/se/users/{TEST_USER_UID}"
    
    update_data = {
        "first_name": "Updated",
        "grade_level": 9,
        "group_ids": ["group3"]
    }
    
    response = requests.put(url, json=update_data)
    assert response.status_code == 200
    
    user_data = response.json()
    assert user_data["first_name"] == update_data["first_name"]
    assert user_data["grade_level"] == update_data["grade_level"]
    assert user_data["group_ids"] == update_data["group_ids"]
    # Unchanged fields should remain the same
    assert user_data["last_name"] == TEST_USER_DATA["last_name"]
    assert user_data["language"] == TEST_USER_DATA["language"]
    assert user_data["preferred_type"] == TEST_USER_DATA["preferred_type"]

def test_update_nonexistent_user():
    """Test updating a user that doesn't exist"""
    url = f"{BASE_URL}/apps/se/users/nonexistent_user"
    
    response = requests.put(url, json={"first_name": "Updated"})
    assert response.status_code == 404

def test_delete_user():
    """Test deleting a user"""
    url = f"{BASE_URL}/apps/se/users/{TEST_USER_UID}"
    
    response = requests.delete(url)
    assert response.status_code == 200
    assert response.json()["message"] == f"SE User {TEST_USER_UID} successfully deleted"

def test_delete_nonexistent_user():
    """Test deleting a user that doesn't exist"""
    url = f"{BASE_URL}/apps/se/users/nonexistent_user"
    
    response = requests.delete(url)
    assert response.status_code == 404

def test_fetch_usage_summary():
    """Test fetching user usage summary"""
    # First create a user
    create_url = f"{BASE_URL}/apps/se/users/{TEST_USER_UID}"
    requests.post(create_url, json=TEST_USER_DATA)
    
    # Test fetching usage summary
    url = f"{BASE_URL}/apps/se/fetch_usage_summary/{TEST_USER_UID}"
    
    response = requests.get(url)
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "usage_summary" in data
    assert isinstance(data["usage_summary"], list)

def test_fetch_usage_summary_nonexistent_user():
    """Test fetching usage summary for a nonexistent user"""
    url = f"{BASE_URL}/apps/se/fetch_usage_summary/nonexistent_user"
    
    response = requests.get(url)
    assert response.status_code == 200  # Should return empty list, not error
    data = response.json()
    assert data["status"] == "success"
    assert data["usage_summary"] == []
