"""
Asynchronous Stories API Integration Tests

Tests for Stories API endpoints that now return TaskResponse objects.
These tests focus on verifying that tasks are properly submitted and 
can be monitored through the Task API.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.main import app
from app.services.task_service import get_task_service


class TestStoriesAPIAsync:
    """Test Stories API endpoints with async task responses."""

    @pytest.fixture
    def mock_task_service_stories(self):
        """Mock TaskService for stories operations."""
        mock_service = Mock()
        
        # Mock story task submissions
        mock_service.create_story_async.return_value = "story-create-task-123"
        mock_service.update_story_async.return_value = "story-update-task-456" 
        mock_service.delete_story_async.return_value = "story-delete-task-789"
        mock_service.patch_story_async.return_value = "story-patch-task-101"
        
        return mock_service

    def test_create_story_async(self, client: TestClient, sample_story_data, mock_task_service_stories):
        """Test creating a story returns task response."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_stories
        try:
            response = client.post("/api/v1/stories/", json=sample_story_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify TaskResponse structure
            assert "task_id" in data
            assert "status" in data  
            assert "message" in data
            assert "estimated_time" in data
            
            assert data["status"] == "PENDING"
            assert data["task_id"] == "story-create-task-123"
            assert "creation" in data["message"].lower()
            assert data["estimated_time"] == 30
            
            # Verify TaskService was called correctly
            mock_task_service_stories.create_story_async.assert_called_once()
            call_args = mock_task_service_stories.create_story_async.call_args[0][0]
            assert call_args["title"] == sample_story_data["title"]
            assert call_args["content"] == sample_story_data["content"]
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_create_story_invalid_data(self, client: TestClient, mock_task_service_stories):
        """Test creating story with invalid data."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_stories
        try:
            # Test empty title
            invalid_data = {"title": "", "content": "Test content", "author": "Test Author"}
            response = client.post("/api/v1/stories/", json=invalid_data)
            
            # Should return validation error before reaching TaskService
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # TaskService should not be called for invalid data
            mock_task_service_stories.create_story_async.assert_not_called()
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_update_story_async(self, client: TestClient, mock_task_service_stories):
        """Test updating a story returns task response.""" 
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_stories
        try:
            story_id = 1
            update_data = {
                "title": "Updated Story Title",
                "content": "Updated content"
            }
            
            response = client.put(f"/api/v1/stories/{story_id}", json=update_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify TaskResponse structure
            assert data["task_id"] == "story-update-task-456"
            assert data["status"] == "PENDING" 
            assert "update" in data["message"].lower()
            assert data["estimated_time"] == 20
            
            # Verify TaskService was called with correct parameters
            mock_task_service_stories.update_story_async.assert_called_once_with(
                story_id, update_data, None
            )
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_delete_story_async(self, client: TestClient, mock_task_service_stories):
        """Test deleting a story returns task response."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_stories
        try:
            story_id = 1
            
            response = client.delete(f"/api/v1/stories/{story_id}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify TaskResponse structure
            assert data["task_id"] == "story-delete-task-789"
            assert data["status"] == "PENDING"
            assert "deletion" in data["message"].lower()
            assert data["estimated_time"] == 15
            
            # Verify TaskService was called correctly
            mock_task_service_stories.delete_story_async.assert_called_once_with(story_id, None)
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_publish_story_async(self, client: TestClient, mock_task_service_stories):
        """Test publishing a story returns task response."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_stories
        try:
            story_id = 1
            
            response = client.patch(f"/api/v1/stories/{story_id}/publish")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify TaskResponse structure
            assert data["task_id"] == "story-patch-task-101"
            assert data["status"] == "PENDING"
            assert "publish" in data["message"].lower()
            assert data["estimated_time"] == 10
            
            # Verify TaskService was called with publish data
            mock_task_service_stories.patch_story_async.assert_called_once_with(
                story_id, {"is_published": True}
            )
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_unpublish_story_async(self, client: TestClient, mock_task_service_stories):
        """Test unpublishing a story returns task response."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_stories
        try:
            story_id = 1
            
            response = client.patch(f"/api/v1/stories/{story_id}/unpublish")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify TaskResponse structure  
            assert data["task_id"] == "story-patch-task-101"
            assert data["status"] == "PENDING"
            assert "unpublish" in data["message"].lower()
            assert data["estimated_time"] == 10
            
            # Verify TaskService was called with unpublish data
            mock_task_service_stories.patch_story_async.assert_called_once_with(
                story_id, {"is_published": False}
            )
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_task_service_error_handling(self, client: TestClient, sample_story_data):
        """Test error handling when TaskService fails."""
        # Mock a failing TaskService
        mock_service = Mock()
        mock_service.create_story_async.side_effect = Exception("TaskService unavailable")
        
        app.dependency_overrides[get_task_service] = lambda: mock_service
        try:
            response = client.post("/api/v1/stories/", json=sample_story_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            
            assert "detail" in data
            assert "Failed to submit story creation task" in data["detail"]
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]


class TestStoriesAPISync:
    """Test synchronous Stories API endpoints (GET operations)."""
    
    def test_get_stories_endpoint_still_sync(self, client: TestClient):
        """Test that GET stories endpoint remains synchronous."""
        response = client.get("/api/v1/stories/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return list directly, not TaskResponse
        assert isinstance(data, list)
        
        # Empty list for clean test database
        assert len(data) == 0

    def test_get_stories_with_parameters(self, client: TestClient):
        """Test GET stories with query parameters."""
        response = client.get("/api/v1/stories/?limit=5&skip=0&published_only=true")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return list, not TaskResponse
        assert isinstance(data, list)

    def test_get_story_by_id_sync(self, client: TestClient):
        """Test that GET story by ID remains synchronous."""
        # Test with non-existent ID (should return 404)
        response = client.get("/api/v1/stories/999")
        
        # This should be 404 for non-existent story, not a task
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        # Should be error response, not TaskResponse
        assert "detail" in data
        assert "task_id" not in data

    def test_get_stories_filter_by_genre(self, client: TestClient, db_session):
        """Test filtering stories by genre."""
        from app.models.story import Story
        
        # Create test stories directly in database
        test_stories = [
            Story(title="Fantasy Adventure", content="A tale of magic", author="Fantasy Author", genre="Fantasy", is_published=True),
            Story(title="Sci-Fi Journey", content="Space exploration", author="Sci-Fi Author", genre="Science Fiction", is_published=True),
            Story(title="Mystery Novel", content="A thrilling mystery", author="Mystery Author", genre="Mystery", is_published=True)
        ]
        
        for story in test_stories:
            db_session.add(story)
        db_session.commit()
        
        # Filter by Fantasy genre
        response = client.get("/api/v1/stories/?genre=Fantasy")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["genre"] == "Fantasy"

    def test_get_stories_filter_by_author(self, client: TestClient, db_session):
        """Test filtering stories by author."""
        from app.models.story import Story
        
        test_stories = [
            Story(title="Story 1", content="Content 1", author="Fantasy Author", genre="Fantasy", is_published=True),
            Story(title="Story 2", content="Content 2", author="Sci-Fi Author", genre="Science Fiction", is_published=True)
        ]
        
        for story in test_stories:
            db_session.add(story)
        db_session.commit()
        
        # Filter by author (partial match)
        response = client.get("/api/v1/stories/?author=Fantasy")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert "Fantasy" in data[0]["author"]

    def test_get_stories_filter_published_only(self, client: TestClient, db_session):
        """Test filtering stories to show only published ones."""
        from app.models.story import Story
        
        test_stories = [
            Story(title="Published Story", content="Content 1", author="Author 1", genre="Fantasy", is_published=True),
            Story(title="Draft Story", content="Content 2", author="Author 2", genre="Mystery", is_published=False),
            Story(title="Another Published", content="Content 3", author="Author 3", genre="Sci-Fi", is_published=True)
        ]
        
        for story in test_stories:
            db_session.add(story)
        db_session.commit()
        
        # Filter published only
        response = client.get("/api/v1/stories/?published_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data) == 2  # Only 2 published stories
        for story in data:
            assert story["is_published"] is True

    def test_get_stories_with_pagination_extended(self, client: TestClient, db_session):
        """Test GET stories with pagination parameters."""
        from app.models.story import Story
        
        # Create multiple test stories
        test_stories = [
            Story(title=f"Story {i}", content=f"Content {i}", author=f"Author {i}", genre="Fantasy", is_published=True)
            for i in range(1, 6)  # Create 5 stories
        ]
        
        for story in test_stories:
            db_session.add(story)
        db_session.commit()
        
        # Test pagination: limit=2, skip=1 
        response = client.get("/api/v1/stories/?limit=2&skip=1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        
        # Test another page
        response = client.get("/api/v1/stories/?limit=3&skip=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_get_story_by_id_with_data(self, client: TestClient, db_session):
        """Test GET story by ID with actual data."""
        from app.models.story import Story
        
        # Create a test story
        story = Story(
            title="Test Story",
            content="Test content",
            author="Test Author", 
            genre="Test Genre",
            is_published=True
        )
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        
        # Get story by ID
        response = client.get(f"/api/v1/stories/{story.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == story.id
        assert data["title"] == "Test Story"
        assert data["content"] == "Test content"
        assert data["author"] == "Test Author"
        assert data["genre"] == "Test Genre"
        assert data["is_published"] is True
