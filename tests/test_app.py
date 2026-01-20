import pytest
from fastapi import HTTPException


class TestRoot:
    """Test root endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test get activities endpoint"""

    def test_get_activities_success(self, client, reset_activities):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # Check that we have activities
        assert len(activities) > 0
        
        # Check structure of an activity
        assert "Chess Club" in activities
        activity = activities["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Test signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=student@test.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "student@test.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_invalid_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Invalid%20Activity/signup?email=student@test.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self, client, reset_activities):
        """Test signup when already registered"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple students can sign up"""
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=student1@test.edu"
        )
        response2 = client.post(
            "/activities/Chess%20Club/signup?email=student2@test.edu"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both were added
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert "student1@test.edu" in chess_club["participants"]
        assert "student2@test.edu" in chess_club["participants"]


class TestUnregister:
    """Test unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_invalid_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Invalid%20Activity/unregister?email=student@test.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister when not registered"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@test.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        
        # Verify they are in the activity
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert email in chess_club["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify they are removed
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert email not in chess_club["participants"]

    def test_signup_then_unregister(self, client, reset_activities):
        """Test signup followed by unregister"""
        email = "newstudent@test.edu"
        
        # Sign up
        response1 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        prog_class = activities_response.json()["Programming Class"]
        assert email in prog_class["participants"]
        
        # Unregister
        response2 = client.post(
            f"/activities/Programming%20Class/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify unregister
        activities_response = client.get("/activities")
        prog_class = activities_response.json()["Programming Class"]
        assert email not in prog_class["participants"]
