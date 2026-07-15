"""Tests for the GET /activities endpoint."""

import pytest


def test_get_activities(client):
    """Test retrieving all activities."""
    response = client.get("/activities")
    assert response.status_code == 200

    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) == 3

    # Check Chess Club exists
    assert "Chess Club" in activities
    assert activities["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert activities["Chess Club"]["max_participants"] == 12
    assert len(activities["Chess Club"]["participants"]) == 2


def test_get_activities_contains_all_fields(client):
    """Test that each activity has all required fields."""
    response = client.get("/activities")
    activities = response.json()

    required_fields = ["description", "schedule", "max_participants", "participants"]

    for activity_name, activity_data in activities.items():
        for field in required_fields:
            assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"


def test_get_activities_participants_is_list(client):
    """Test that participants field is a list."""
    response = client.get("/activities")
    activities = response.json()

    for activity_name, activity_data in activities.items():
        assert isinstance(
            activity_data["participants"], list
        ), f"Participants for '{activity_name}' should be a list"


def test_get_activities_max_participants_is_int(client):
    """Test that max_participants is an integer."""
    response = client.get("/activities")
    activities = response.json()

    for activity_name, activity_data in activities.items():
        assert isinstance(
            activity_data["max_participants"], int
        ), f"max_participants for '{activity_name}' should be an integer"
