import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Club" in data

def test_signup_for_activity_success():
    email = "testuser@mergington.edu"
    activity = "Basketball Club"
    # Remove if already present
    client.delete(f"/activities/{activity}/unregister?email={email}")
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]
    # Clean up
    client.delete(f"/activities/{activity}/unregister?email={email}")

def test_signup_for_activity_duplicate():
    email = "testdup@mergington.edu"
    activity = "Soccer Team"
    # Ensure user is signed up
    client.post(f"/activities/{activity}/signup?email={email}")
    # Try to sign up again
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    # Clean up
    client.delete(f"/activities/{activity}/unregister?email={email}")

def test_signup_for_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=foo@bar.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_participant():
    email = "unregtest@mergington.edu"
    activity = "Art Club"
    # Ensure user is signed up
    client.post(f"/activities/{activity}/signup?email={email}")
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code in (200, 404)  # 404 if already removed
    # Should not be in participants
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
