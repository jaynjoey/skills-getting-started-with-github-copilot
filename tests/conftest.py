"""Pytest configuration and shared fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import FastAPI


@pytest.fixture
def test_app():
    """Create a fresh FastAPI app instance for testing with isolated data."""
    app = FastAPI(
        title="Mergington High School API",
        description="API for viewing and signing up for extracurricular activities",
    )

    # In-memory activity database for testing
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        },
    }

    # Import endpoints and routes
    from fastapi import HTTPException
    from fastapi.responses import RedirectResponse

    @app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")

    @app.get("/activities")
    def get_activities():
        return test_activities

    @app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        activity = test_activities[activity_name]

        if email in activity["participants"]:
            raise HTTPException(
                status_code=400, detail="Student already signed up for this activity"
            )

        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}

    @app.delete("/activities/{activity_name}/participant")
    def remove_participant(activity_name: str, email: str):
        """Remove a student from an activity"""
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        activity = test_activities[activity_name]

        if email not in activity["participants"]:
            raise HTTPException(
                status_code=400, detail="Student not signed up for this activity"
            )

        activity["participants"].remove(email)
        return {"message": f"Removed {email} from {activity_name}"}

    return app


@pytest.fixture
def client(test_app):
    """Create a TestClient for testing the FastAPI app."""
    return TestClient(test_app)
