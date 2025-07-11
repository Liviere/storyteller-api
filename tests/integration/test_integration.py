"""
Integration tests for Story Teller API.
"""

import pytest
from fastapi import status


class TestIntegration:
    """Integration test cases that test multiple components together."""

    def test_complete_story_workflow(self, client):
        """Test complete story lifecycle: create, read, update, publish, delete."""
        # 1. Create a story
        story_data = {
            "title": "Integration Test Story",
            "content": "This is a story for integration testing.",
            "author": "Integration Tester",
            "genre": "Test",
            "is_published": False,
        }

        create_response = client.post("/api/v1/stories/", json=story_data)
        assert create_response.status_code == status.HTTP_200_OK
        created_story = create_response.json()
        story_id = created_story["id"]

        # 2. Read the story
        get_response = client.get(f"/api/v1/stories/{story_id}")
        assert get_response.status_code == status.HTTP_200_OK
        retrieved_story = get_response.json()
        assert retrieved_story["title"] == story_data["title"]
        assert retrieved_story["is_published"] is False

        # 3. Update the story
        update_data = {
            "title": "Updated Integration Test Story",
            "content": "This story has been updated during integration testing.",
        }
        update_response = client.put(f"/api/v1/stories/{story_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        updated_story = update_response.json()
        assert updated_story["title"] == update_data["title"]
        assert updated_story["content"] == update_data["content"]
        assert (
            updated_story["author"] == story_data["author"]
        )  # Should remain unchanged

        # 4. Publish the story
        publish_response = client.patch(f"/api/v1/stories/{story_id}/publish")
        assert publish_response.status_code == status.HTTP_200_OK
        publish_data = publish_response.json()
        assert publish_data["story"]["is_published"] is True

        # 5. Verify it appears in published stories
        published_response = client.get("/api/v1/stories/?published_only=true")
        assert published_response.status_code == status.HTTP_200_OK
        published_stories = published_response.json()
        assert len(published_stories) == 1
        assert published_stories[0]["id"] == story_id

        # 6. Unpublish the story
        unpublish_response = client.patch(f"/api/v1/stories/{story_id}/unpublish")
        assert unpublish_response.status_code == status.HTTP_200_OK
        unpublish_data = unpublish_response.json()
        assert unpublish_data["story"]["is_published"] is False

        # 7. Delete the story
        delete_response = client.delete(f"/api/v1/stories/{story_id}")
        assert delete_response.status_code == status.HTTP_200_OK

        # 8. Verify it's deleted
        get_deleted_response = client.get(f"/api/v1/stories/{story_id}")
        assert get_deleted_response.status_code == status.HTTP_404_NOT_FOUND

    def test_multiple_stories_with_filtering(self, client):
        """Test creating multiple stories and filtering them."""
        # Create multiple stories with different attributes
        stories_data = [
            {
                "title": "Fantasy Epic",
                "content": "A tale of magic and adventure.",
                "author": "Fantasy Writer",
                "genre": "Fantasy",
                "is_published": True,
            },
            {
                "title": "Sci-Fi Adventure",
                "content": "A journey through space and time.",
                "author": "Sci-Fi Writer",
                "genre": "Science Fiction",
                "is_published": False,
            },
            {
                "title": "Another Fantasy",
                "content": "More magic and dragons.",
                "author": "Another Fantasy Writer",
                "genre": "Fantasy",
                "is_published": True,
            },
            {
                "title": "Mystery Novel",
                "content": "A thrilling mystery.",
                "author": "Mystery Writer",
                "genre": "Mystery",
                "is_published": False,
            },
        ]

        created_story_ids = []
        for story_data in stories_data:
            response = client.post("/api/v1/stories/", json=story_data)
            assert response.status_code == status.HTTP_200_OK
            created_story_ids.append(response.json()["id"])

        # Test getting all stories
        all_response = client.get("/api/v1/stories/")
        assert all_response.status_code == status.HTTP_200_OK
        all_stories = all_response.json()
        assert len(all_stories) == 4

        # Test filtering by genre
        fantasy_response = client.get("/api/v1/stories/?genre=Fantasy")
        assert fantasy_response.status_code == status.HTTP_200_OK
        fantasy_stories = fantasy_response.json()
        assert len(fantasy_stories) == 2
        for story in fantasy_stories:
            assert story["genre"] == "Fantasy"

        # Test filtering by author (partial match)
        fantasy_author_response = client.get("/api/v1/stories/?author=Fantasy")
        assert fantasy_author_response.status_code == status.HTTP_200_OK
        fantasy_author_stories = fantasy_author_response.json()
        assert len(fantasy_author_stories) == 2
        for story in fantasy_author_stories:
            assert "Fantasy" in story["author"]

        # Test filtering published only
        published_response = client.get("/api/v1/stories/?published_only=true")
        assert published_response.status_code == status.HTTP_200_OK
        published_stories = published_response.json()
        assert len(published_stories) == 2
        for story in published_stories:
            assert story["is_published"] is True

        # Test pagination
        paginated_response = client.get("/api/v1/stories/?limit=2")
        assert paginated_response.status_code == status.HTTP_200_OK
        paginated_stories = paginated_response.json()
        assert len(paginated_stories) == 2

        # Test combining filters
        combined_response = client.get(
            "/api/v1/stories/?genre=Fantasy&published_only=true"
        )
        assert combined_response.status_code == status.HTTP_200_OK
        combined_stories = combined_response.json()
        assert len(combined_stories) == 2
        for story in combined_stories:
            assert story["genre"] == "Fantasy"
            assert story["is_published"] is True

        # Clean up - delete all created stories
        for story_id in created_story_ids:
            delete_response = client.delete(f"/api/v1/stories/{story_id}")
            assert delete_response.status_code == status.HTTP_200_OK

    def test_error_handling_workflow(self, client):
        """Test error handling in various scenarios."""
        # Test creating story with invalid data
        invalid_story_data = {
            "title": "",  # Invalid: empty title
            "content": "Test content",
            "author": "Test Author",
        }

        create_response = client.post("/api/v1/stories/", json=invalid_story_data)
        assert create_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test operations on non-existent story
        non_existent_id = 99999

        # Get non-existent story
        get_response = client.get(f"/api/v1/stories/{non_existent_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

        # Update non-existent story
        update_data = {"title": "Updated Title"}
        update_response = client.put(
            f"/api/v1/stories/{non_existent_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_404_NOT_FOUND

        # Delete non-existent story
        delete_response = client.delete(f"/api/v1/stories/{non_existent_id}")
        assert delete_response.status_code == status.HTTP_404_NOT_FOUND

        # Publish non-existent story
        publish_response = client.patch(f"/api/v1/stories/{non_existent_id}/publish")
        assert publish_response.status_code == status.HTTP_404_NOT_FOUND

        # Unpublish non-existent story
        unpublish_response = client.patch(
            f"/api/v1/stories/{non_existent_id}/unpublish"
        )
        assert unpublish_response.status_code == status.HTTP_404_NOT_FOUND
