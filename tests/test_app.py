import sys
from pathlib import Path
import copy

# Add src/ to path so we can import the application module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from app import app, activities
from fastapi.testclient import TestClient
import pytest


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_success(client):
    email = "newstudent@mergington.edu"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert resp.json()["message"] == f"Signed up {email} for Chess Club"


def test_signup_already_signed(client):
    resp = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
    assert resp.status_code == 400


def test_signup_activity_not_found(client):
    resp = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_remove_participant_success(client):
    email = "michael@mergington.edu"
    resp = client.delete("/activities/Chess Club/participants", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_remove_participant_not_found(client):
    resp = client.delete("/activities/Chess Club/participants", params={"email": "noone@x.com"})
    assert resp.status_code == 404


def test_root_redirect(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307, 308)
    # follow redirect and check content
    follow = client.get(resp.headers["location"])
    assert follow.status_code == 200
    assert "text/html" in follow.headers.get("content-type", "")
