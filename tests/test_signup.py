"""Tests for the POST /activities/{activity_name}/signup endpoint."""

import pytest


def test_signup_new_participant(client):
    """Test successfully signing up a new participant."""
    response = client.post(
        "/activities/Chess%20Club/signup?email=alex@mergington.edu"
    )
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "alex@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]

    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "alex@mergington.edu" in activities["Chess Club"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == 3


def test_signup_duplicate_participant(client):
    """Test that duplicate signups are rejected."""
    # michael@mergington.edu is already in Chess Club
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_activity_not_found(client):
    """Test signup fails for non-existent activity."""
    response = client.post(
        "/activities/NonExistent%20Club/signup?email=alex@mergington.edu"
    )
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_multiple_different_activities(client):
    """Test that same participant can sign up for multiple activities."""
    email = "newstudent@mergington.edu"

    # Sign up for Chess Club
    response1 = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )
    assert response1.status_code == 200

    # Sign up for Programming Class
    response2 = client.post(
        f"/activities/Programming%20Class/signup?email={email}"
    )
    assert response2.status_code == 200

    # Verify both signups succeeded
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities["Chess Club"]["participants"]
    assert email in activities["Programming Class"]["participants"]


def test_signup_preserves_existing_participants(client):
    """Test that signup doesn't affect other participants."""
    # Get original participant count
    response_before = client.get("/activities")
    original_count = len(response_before.json()["Gym Class"]["participants"])

    # Sign up new participant for different activity
    client.post("/activities/Chess%20Club/signup?email=newemail@mergington.edu")

    # Verify Gym Class participants unchanged
    response_after = client.get("/activities")
    assert len(response_after.json()["Gym Class"]["participants"]) == original_count
