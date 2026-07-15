"""Tests for the DELETE /activities/{activity_name}/participant endpoint."""

import pytest


def test_delete_existing_participant(client):
    """Test successfully removing an existing participant."""
    # michael@mergington.edu is in Chess Club initially
    response = client.delete(
        "/activities/Chess%20Club/participant?email=michael@mergington.edu"
    )
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "michael@mergington.edu" in data["message"]
    assert "Removed" in data["message"]

    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == 1


def test_delete_participant_not_signed_up(client):
    """Test that deleting a non-participant fails."""
    response = client.delete(
        "/activities/Chess%20Club/participant?email=alex@mergington.edu"
    )
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_delete_activity_not_found(client):
    """Test delete fails for non-existent activity."""
    response = client.delete(
        "/activities/NonExistent%20Club/participant?email=michael@mergington.edu"
    )
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_delete_then_signup_same_participant(client):
    """Test that a participant can be removed and re-signed up."""
    email = "michael@mergington.edu"
    activity = "Chess%20Club"

    # Remove participant
    delete_response = client.delete(
        f"/activities/{activity}/participant?email={email}"
    )
    assert delete_response.status_code == 200

    # Verify removed
    activities_response = client.get("/activities")
    assert email not in activities_response.json()["Chess Club"]["participants"]

    # Re-sign up same participant
    signup_response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert signup_response.status_code == 200

    # Verify re-signed up
    activities_response = client.get("/activities")
    assert email in activities_response.json()["Chess Club"]["participants"]


def test_delete_preserves_other_participants(client):
    """Test that deleting one participant doesn't affect others."""
    # Get initial state
    response_before = client.get("/activities")
    initial_participants = response_before.json()["Chess Club"]["participants"].copy()

    # Delete michael@mergington.edu
    client.delete("/activities/Chess%20Club/participant?email=michael@mergington.edu")

    # Verify daniel is still there
    response_after = client.get("/activities")
    remaining = response_after.json()["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in remaining
    assert len(remaining) == len(initial_participants) - 1


def test_delete_multiple_participants_sequentially(client):
    """Test deleting multiple participants one by one."""
    participants_to_delete = ["michael@mergington.edu", "daniel@mergington.edu"]

    for email in participants_to_delete:
        response = client.delete(
            f"/activities/Chess%20Club/participant?email={email}"
        )
        assert response.status_code == 200

    # Verify all deleted
    activities_response = client.get("/activities")
    assert len(activities_response.json()["Chess Club"]["participants"]) == 0
