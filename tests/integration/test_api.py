"""
Tests for Stories API endpoints.
"""

import pytest
from fastapi import status


class TestStoriesAPI:
    """Test cases for Stories API endpoints."""

    def test_create_story(self, client, sample_story_data):
        """Test creating a new story."""
        response = client.post("/api/v1/stories/", json=sample_story_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["title"] == sample_story_data["title"]
        assert data["content"] == sample_story_data["content"]
        assert data["author"] == sample_story_data["author"]
        assert data["genre"] == sample_story_data["genre"]
        assert data["is_published"] == sample_story_data["is_published"]
        assert "id" in data
        assert "created_at" in data

    def test_create_story_invalid_data(self, client):
        """Test creating a story with invalid data."""
        # Test empty title
        invalid_data = {"title": "", "content": "Test content", "author": "Test Author"}
        response = client.post("/api/v1/stories/", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test missing required field
        invalid_data = {
            "title": "Test Title",
            "content": "Test content",
            # Missing author
        }
        response = client.post("/api/v1/stories/", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_stories_empty(self, client):
        """Test getting stories when database is empty."""
        response = client.get("/api/v1/stories/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    def test_get_stories(self, client, sample_stories_data):
        """Test getting all stories."""
        # Create test stories
        created_stories = []
        for story_data in sample_stories_data:
            response = client.post("/api/v1/stories/", json=story_data)
            assert response.status_code == status.HTTP_200_OK
            created_stories.append(response.json())

        # Get all stories
        response = client.get("/api/v1/stories/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(sample_stories_data)

    def test_get_stories_with_pagination(self, client, sample_stories_data):
        """Test getting stories with pagination."""
        # Create test stories
        for story_data in sample_stories_data:
            response = client.post("/api/v1/stories/", json=story_data)
            assert response.status_code == status.HTTP_200_OK

        # Test limit
        response = client.get("/api/v1/stories/?limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

        # Test skip
        response = client.get("/api/v1/stories/?skip=1&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_stories_filter_by_genre(self, client, sample_stories_data):
        """Test filtering stories by genre."""
        # Create test stories
        for story_data in sample_stories_data:
            response = client.post("/api/v1/stories/", json=story_data)
            assert response.status_code == status.HTTP_200_OK

        # Filter by Fantasy genre
        response = client.get("/api/v1/stories/?genre=Fantasy")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["genre"] == "Fantasy"

    def test_get_stories_filter_by_author(self, client, sample_stories_data):
        """Test filtering stories by author."""
        # Create test stories
        for story_data in sample_stories_data:
            response = client.post("/api/v1/stories/", json=story_data)
            assert response.status_code == status.HTTP_200_OK

        # Filter by author (partial match)
        response = client.get("/api/v1/stories/?author=Fantasy")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert "Fantasy" in data[0]["author"]

    def test_get_stories_filter_published_only(self, client, sample_stories_data):
        """Test filtering stories to show only published ones."""
        # Create test stories
        for story_data in sample_stories_data:
            response = client.post("/api/v1/stories/", json=story_data)
            assert response.status_code == status.HTTP_200_OK

        # Filter published only
        response = client.get("/api/v1/stories/?published_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Count published stories in sample data
        published_count = sum(
            1 for story in sample_stories_data if story["is_published"]
        )
        assert len(data) == published_count

        for story in data:
            assert story["is_published"] is True

    def test_get_story_by_id(self, client, sample_story_data):
        """Test getting a specific story by ID."""
        # Create a story
        create_response = client.post("/api/v1/stories/", json=sample_story_data)
        assert create_response.status_code == status.HTTP_200_OK
        created_story = create_response.json()
        story_id = created_story["id"]

        # Get the story
        response = client.get(f"/api/v1/stories/{story_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == story_id
        assert data["title"] == sample_story_data["title"]
        assert data["content"] == sample_story_data["content"]

    def test_get_story_not_found(self, client):
        """Test getting a non-existent story."""
        response = client.get("/api/v1/stories/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_story(self, client, sample_story_data):
        """Test updating a story."""
        # Create a story
        create_response = client.post("/api/v1/stories/", json=sample_story_data)
        assert create_response.status_code == status.HTTP_200_OK
        created_story = create_response.json()
        story_id = created_story["id"]

        # Update the story
        update_data = {"title": "Updated Title", "content": "Updated content"}
        response = client.put(f"/api/v1/stories/{story_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        updated_story = response.json()
        assert updated_story["title"] == "Updated Title"
        assert updated_story["content"] == "Updated content"
        assert updated_story["author"] == sample_story_data["author"]  # Unchanged

    def test_update_story_not_found(self, client):
        """Test updating a non-existent story."""
        update_data = {"title": "Updated Title"}
        response = client.put("/api/v1/stories/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_story(self, client, sample_story_data):
        """Test deleting a story."""
        # Create a story
        create_response = client.post("/api/v1/stories/", json=sample_story_data)
        assert create_response.status_code == status.HTTP_200_OK
        created_story = create_response.json()
        story_id = created_story["id"]

        # Delete the story
        response = client.delete(f"/api/v1/stories/{story_id}")
        assert response.status_code == status.HTTP_200_OK

        # Verify it's deleted
        get_response = client.get(f"/api/v1/stories/{story_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_story_not_found(self, client):
        """Test deleting a non-existent story."""
        response = client.delete("/api/v1/stories/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_publish_story(self, client, sample_story_data):
        """Test publishing a story."""
        # Create an unpublished story
        sample_story_data["is_published"] = False
        create_response = client.post("/api/v1/stories/", json=sample_story_data)
        assert create_response.status_code == status.HTTP_200_OK
        created_story = create_response.json()
        story_id = created_story["id"]
        assert created_story["is_published"] is False

        # Publish the story
        response = client.patch(f"/api/v1/stories/{story_id}/publish")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["story"]["is_published"] is True

    def test_unpublish_story(self, client, sample_story_data):
        """Test unpublishing a story."""
        # Create a published story
        sample_story_data["is_published"] = True
        create_response = client.post("/api/v1/stories/", json=sample_story_data)
        assert create_response.status_code == status.HTTP_200_OK
        created_story = create_response.json()
        story_id = created_story["id"]
        assert created_story["is_published"] is True

        # Unpublish the story
        response = client.patch(f"/api/v1/stories/{story_id}/unpublish")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["story"]["is_published"] is False

    def test_publish_story_not_found(self, client):
        """Test publishing a non-existent story."""
        response = client.patch("/api/v1/stories/999/publish")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unpublish_story_not_found(self, client):
        """Test unpublishing a non-existent story."""
        response = client.patch("/api/v1/stories/999/unpublish")
        assert response.status_code == status.HTTP_404_NOT_FOUND
