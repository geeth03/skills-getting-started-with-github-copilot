import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Arrange: Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        # Arrange: Client is provided by fixture
        
        # Act: Fetch all activities
        response = client.get("/activities")
        
        # Assert: Verify response status and content
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities
    
    def test_get_activities_contains_required_fields(self, client):
        # Arrange: Client is provided by fixture
        
        # Act: Fetch all activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify each activity has required fields
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        # Arrange: Client is provided by fixture
        
        # Act: Access root path with follow_redirects=False to check redirect
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify it redirects to static index
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_valid_email_adds_participant(self, client):
        # Arrange: Set up test data
        activity_name = "Chess Club"
        test_email = "newstudent@mergington.edu"
        
        # Act: Sign up the student
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        # Assert: Verify signup succeeds and participant is added
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {test_email} for {activity_name}"
        
        # Verify participant was added to activity
        activities = client.get("/activities").json()
        assert test_email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_email_returns_400(self, client):
        # Arrange: Use an email already registered
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act: Attempt to sign up with duplicate email
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        
        # Assert: Verify 400 error is returned
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_invalid_activity_returns_404(self, client):
        # Arrange: Use non-existent activity name
        invalid_activity = "Nonexistent Activity"
        test_email = "student@mergington.edu"
        
        # Act: Attempt to sign up for invalid activity
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={test_email}"
        )
        
        # Assert: Verify 404 error is returned
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_removes_participant(self, client):
        # Arrange: First sign up a student
        activity_name = "Chess Club"
        test_email = "unregister_test@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Act: Unregister the student
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={test_email}"
        )
        
        # Assert: Verify unregister succeeds and participant is removed
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {test_email} from {activity_name}"
        
        # Verify participant was removed from activity
        activities = client.get("/activities").json()
        assert test_email not in activities[activity_name]["participants"]
    
    def test_unregister_non_registered_email_returns_400(self, client):
        # Arrange: Use email not registered for activity
        activity_name = "Tennis Club"
        unregistered_email = "notregistered@mergington.edu"
        
        # Act: Attempt to unregister email that isn't registered
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={unregistered_email}"
        )
        
        # Assert: Verify 400 error is returned
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_invalid_activity_returns_404(self, client):
        # Arrange: Use non-existent activity name
        invalid_activity = "Nonexistent Activity"
        test_email = "student@mergington.edu"
        
        # Act: Attempt to unregister from invalid activity
        response = client.delete(
            f"/activities/{invalid_activity}/unregister?email={test_email}"
        )
        
        # Assert: Verify 404 error is returned
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
