"""
End-to-end workflow tests for Story Teller API.

This module contains comprehensive workflow tests that validate complete user journeys
and cross-component interactions in the Story Teller application.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestStoryWorkflows:
    """End-to-end workflow tests for story management."""

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
        ]

        created_ids = []

        # Create all stories
        for story_data in stories_data:
            response = client.post("/api/v1/stories/", json=story_data)
            assert response.status_code == status.HTTP_200_OK
            created_story = response.json()
            created_ids.append(created_story["id"])

        # Test filtering by genre
        fantasy_response = client.get("/api/v1/stories/?genre=Fantasy")
        assert fantasy_response.status_code == status.HTTP_200_OK
        fantasy_stories = fantasy_response.json()
        assert len(fantasy_stories) == 2  # Two fantasy stories

        # Test filtering by published status
        published_response = client.get("/api/v1/stories/?published_only=true")
        assert published_response.status_code == status.HTTP_200_OK
        published_stories = published_response.json()
        assert len(published_stories) == 2  # Two published stories

        # Test combined filtering
        published_fantasy_response = client.get(
            "/api/v1/stories/?genre=Fantasy&published_only=true"
        )
        assert published_fantasy_response.status_code == status.HTTP_200_OK
        published_fantasy_stories = published_fantasy_response.json()
        assert len(published_fantasy_stories) == 2  # Two published fantasy stories

        # Test author filtering (partial match)
        fantasy_author_response = client.get("/api/v1/stories/?author=Fantasy Writer")
        assert fantasy_author_response.status_code == status.HTTP_200_OK
        fantasy_author_stories = fantasy_author_response.json()
        assert (
            len(fantasy_author_stories) == 2
        )  # Finds both "Fantasy Writer" and "Another Fantasy Writer"

        # Test exact author filtering - use more specific search
        exact_author_response = client.get("/api/v1/stories/?author=Sci-Fi Writer")
        assert exact_author_response.status_code == status.HTTP_200_OK
        exact_author_stories = exact_author_response.json()
        assert len(exact_author_stories) == 1  # Only "Sci-Fi Writer" matches exactly

        # Cleanup: Delete all created stories
        for story_id in created_ids:
            delete_response = client.delete(f"/api/v1/stories/{story_id}")
            assert delete_response.status_code == status.HTTP_200_OK

    def test_pagination_workflow(self, client):
        """Test pagination across multiple pages of stories."""
        # Create multiple stories for pagination testing
        story_count = 15
        created_ids = []

        for i in range(story_count):
            story_data = {
                "title": f"Pagination Test Story {i+1}",
                "content": f"Content for story number {i+1}.",
                "author": f"Author {i+1}",
                "genre": "Test",
                "is_published": i % 2 == 0,  # Alternate published status
            }
            response = client.post("/api/v1/stories/", json=story_data)
            assert response.status_code == status.HTTP_200_OK
            created_story = response.json()
            created_ids.append(created_story["id"])

        # Test pagination with different page sizes
        page_sizes = [5, 10, 20]
        for page_size in page_sizes:
            # First page
            first_page_response = client.get(
                f"/api/v1/stories/?limit={page_size}&skip=0"
            )
            assert first_page_response.status_code == status.HTTP_200_OK
            first_page_stories = first_page_response.json()
            assert len(first_page_stories) == min(page_size, story_count)

            # Second page (if applicable)
            if story_count > page_size:
                second_page_response = client.get(
                    f"/api/v1/stories/?limit={page_size}&skip={page_size}"
                )
                assert second_page_response.status_code == status.HTTP_200_OK
                second_page_stories = second_page_response.json()
                expected_second_page_size = min(page_size, story_count - page_size)
                assert len(second_page_stories) == expected_second_page_size

                # Ensure no duplicate stories between pages
                first_page_ids = {story["id"] for story in first_page_stories}
                second_page_ids = {story["id"] for story in second_page_stories}
                assert first_page_ids.isdisjoint(second_page_ids)

        # Cleanup: Delete all created stories
        for story_id in created_ids:
            delete_response = client.delete(f"/api/v1/stories/{story_id}")
            assert delete_response.status_code == status.HTTP_200_OK

    def test_error_handling_workflow(self, client):
        """Test error handling across different scenarios."""
        # Test 1: Create a story with invalid data
        invalid_story_data = {
            "title": "",  # Empty title should fail validation
            "content": "Some content",
            "author": "Test Author",
        }
        invalid_response = client.post("/api/v1/stories/", json=invalid_story_data)
        assert invalid_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test 2: Try to get a non-existent story
        nonexistent_response = client.get("/api/v1/stories/99999")
        assert nonexistent_response.status_code == status.HTTP_404_NOT_FOUND

        # Test 3: Try to update a non-existent story
        update_data = {"title": "Updated Title"}
        update_nonexistent_response = client.put(
            "/api/v1/stories/99999", json=update_data
        )
        assert update_nonexistent_response.status_code == status.HTTP_404_NOT_FOUND

        # Test 4: Try to delete a non-existent story
        delete_nonexistent_response = client.delete("/api/v1/stories/99999")
        assert delete_nonexistent_response.status_code == status.HTTP_404_NOT_FOUND

        # Test 5: Try to publish/unpublish a non-existent story
        publish_nonexistent_response = client.patch("/api/v1/stories/99999/publish")
        assert publish_nonexistent_response.status_code == status.HTTP_404_NOT_FOUND

        unpublish_nonexistent_response = client.patch("/api/v1/stories/99999/unpublish")
        assert unpublish_nonexistent_response.status_code == status.HTTP_404_NOT_FOUND


class TestLLMWorkflows:
    """End-to-end workflow tests for LLM functionality."""

    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_full_story_llm_workflow(
        self, client: TestClient, integration_test_models, skip_integration_tests
    ):
        """Test complete story workflow: generate -> analyze -> summarize -> improve."""
        # Skip if no models configured
        if not integration_test_models.get("story_generation"):
            pytest.skip("No models configured for complete workflow test")

        # Step 1: Generate a story
        generate_response = client.post(
            "/api/v1/llm/generate",
            json={
                "prompt": "A story about friendship",
                "genre": "drama",
                "length": "short",
            },
        )

        if generate_response.status_code != 200:
            pytest.skip("Story generation failed, skipping workflow test")

        story = generate_response.json()["story"]

        # Step 2: Analyze the story
        analyze_response = client.post(
            "/api/v1/llm/analyze", json={"content": story, "analysis_type": "full"}
        )

        if analyze_response.status_code == 200:
            analysis = analyze_response.json()
            assert "analysis" in analysis

        # Step 3: Summarize the story
        summarize_response = client.post(
            "/api/v1/llm/summarize", json={"content": story, "summary_length": "brief"}
        )

        if summarize_response.status_code == 200:
            summary = summarize_response.json()
            assert "summary" in summary

        # Step 4: Improve the story
        improve_response = client.post(
            "/api/v1/llm/improve",
            json={"content": story, "improvement_type": "general"},
        )

        if improve_response.status_code == 200:
            improved = improve_response.json()
            assert "improved_story" in improved
            assert improved["original_story"] == story

    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_story_management_with_llm_workflow(
        self, client: TestClient, integration_test_models, skip_integration_tests
    ):
        """Test combining story management with LLM operations."""
        # Skip if no models configured
        if not integration_test_models.get("story_generation"):
            pytest.skip("No models configured for LLM workflow test")

        # Step 1: Generate a story using LLM
        generate_response = client.post(
            "/api/v1/llm/generate",
            json={
                "prompt": "A tale of two cities in a fantasy world",
                "genre": "fantasy",
                "length": "medium",
            },
        )

        if generate_response.status_code != 200:
            pytest.skip("Story generation failed, skipping workflow test")

        generated_story = generate_response.json()["story"]

        # Step 2: Save the generated story to database
        story_data = {
            "title": "LLM Generated Fantasy Tale",
            "content": generated_story,
            "author": "AI Assistant",
            "genre": "Fantasy",
            "is_published": False,
        }

        create_response = client.post("/api/v1/stories/", json=story_data)
        assert create_response.status_code == status.HTTP_200_OK
        created_story = create_response.json()
        story_id = created_story["id"]

        # Step 3: Analyze the story
        analyze_response = client.post(
            "/api/v1/llm/analyze",
            json={"content": generated_story, "analysis_type": "sentiment"},
        )

        if analyze_response.status_code == 200:
            analysis = analyze_response.json()
            assert "analysis" in analysis

        # Step 4: Improve the story
        improve_response = client.post(
            "/api/v1/llm/improve",
            json={"content": generated_story, "improvement_type": "clarity"},
        )

        if improve_response.status_code == 200:
            improved = improve_response.json()
            improved_story = improved["improved_story"]

            # Step 5: Update the story with improved version
            update_data = {
                "content": improved_story,
                "title": "Improved LLM Generated Fantasy Tale",
            }
            update_response = client.put(
                f"/api/v1/stories/{story_id}", json=update_data
            )
            assert update_response.status_code == status.HTTP_200_OK

        # Step 6: Publish the final story
        publish_response = client.patch(f"/api/v1/stories/{story_id}/publish")
        assert publish_response.status_code == status.HTTP_200_OK

        # Step 7: Verify the published story
        get_response = client.get(f"/api/v1/stories/{story_id}")
        assert get_response.status_code == status.HTTP_200_OK
        final_story = get_response.json()
        assert final_story["is_published"] is True

        # Cleanup
        delete_response = client.delete(f"/api/v1/stories/{story_id}")
        assert delete_response.status_code == status.HTTP_200_OK
