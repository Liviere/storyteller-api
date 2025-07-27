"""
Integration tests for Stories API with real Celery workers.
These tests verify that async operations actually complete and produce correct results.
"""
import time

import pytest
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from fastapi.testclient import TestClient

from app.models.story import Story


@pytest.mark.e2e
class TestStoriesIntegrationCelery:
    """Integration tests for Stories API with real Celery workers."""

    def test_create_story_end_to_end(self, client: TestClient, db_session: Session, sample_story_data):
        """Test complete story creation workflow with real worker."""
        # 1. Submit story creation task
        response = client.post("/api/v1/stories/", json=sample_story_data)
        
        assert response.status_code == 200
        task_response = response.json()
        
        # Verify TaskResponse structure
        assert "task_id" in task_response
        assert "status" in task_response
        assert task_response["status"] == "PENDING"
        
        task_id = task_response["task_id"]
        
        # 2. Wait for task completion
        result = AsyncResult(task_id)
        
        # Poll for result with timeout
        timeout = 30
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        assert result.ready(), f"Task {task_id} did not complete within {timeout} seconds"
        assert result.successful(), f"Task {task_id} failed: {result.traceback}"
        
        # 3. Get task result
        task_result = result.get(timeout=5)
        assert "id" in task_result
        story_id = task_result["id"]
        
        # 4. Verify story was actually created in database
        created_story = db_session.query(Story).filter(Story.id == story_id).first()
        assert created_story is not None
        assert created_story.title == sample_story_data["title"]
        assert created_story.content == sample_story_data["content"]
        assert created_story.author == sample_story_data["author"]
        assert created_story.genre == sample_story_data["genre"]
        assert created_story.is_published == sample_story_data["is_published"]

    def test_update_story_end_to_end(self, client: TestClient, sample_story_data, db_session: Session):
        """Test complete story update workflow with real worker."""
        # 1. First create a story synchronously for testing
        story = Story(**sample_story_data)
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        
        # 2. Submit update task
        update_data = {
            "title": "Updated Title via Celery",
            "content": "Updated content via async worker"
        }
        
        response = client.put(f"/api/v1/stories/{story.id}", json=update_data)
        assert response.status_code == 200
        
        task_response = response.json()
        task_id = task_response["task_id"]
        
        # 3. Wait for task completion
        result = AsyncResult(task_id)
        timeout = 30
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        assert result.ready(), f"Update task {task_id} did not complete"
        assert result.successful(), f"Update task failed: {result.traceback}"
        
        # Store the story ID before expunging
        story_id = story.id
        
        # 4. Verify story was actually updated in database
        db_session.commit()  # Ensure we see committed changes
        db_session.expunge(story)  # Remove from session cache
        updated_story = db_session.query(Story).filter(Story.id == story_id).first()
        assert updated_story is not None
        assert updated_story.title == "Updated Title via Celery"
        assert updated_story.content == "Updated content via async worker"
        # Verify unchanged fields
        assert updated_story.author == sample_story_data["author"]
        assert updated_story.genre == sample_story_data["genre"]

    def test_delete_story_end_to_end(self, client: TestClient, sample_story_data, db_session: Session):
        """Test complete story deletion workflow with real worker."""
        # 1. Create a story to delete
        story = Story(**sample_story_data)
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        story_id = story.id
        
        # 2. Submit deletion task
        response = client.delete(f"/api/v1/stories/{story_id}")
        assert response.status_code == 200
        
        task_response = response.json()
        task_id = task_response["task_id"]
        
        # 3. Wait for task completion
        result = AsyncResult(task_id)
        timeout = 30
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        assert result.ready(), f"Delete task {task_id} did not complete"
        assert result.successful(), f"Delete task failed: {result.traceback}"
        
        # 4. Verify story was actually deleted from database
        db_session.commit()  # Ensure we see committed changes
        deleted_story = db_session.query(Story).filter(Story.id == story_id).first()
        assert deleted_story is None
        
        # 5. Verify GET endpoint returns 404
        get_response = client.get(f"/api/v1/stories/{story_id}")
        assert get_response.status_code == 404

    def test_publish_story_end_to_end(self, client: TestClient, sample_story_data, db_session: Session):
        """Test complete story publishing workflow with real worker."""
        # 1. Create unpublished story
        sample_story_data["is_published"] = False
        story = Story(**sample_story_data)
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        
        assert story.is_published is False
        
        # 2. Submit publish task
        response = client.patch(f"/api/v1/stories/{story.id}/publish")
        assert response.status_code == 200
        
        task_response = response.json()
        task_id = task_response["task_id"]
        
        # 3. Wait for task completion
        result = AsyncResult(task_id)
        timeout = 30
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        assert result.ready(), f"Publish task {task_id} did not complete"
        assert result.successful(), f"Publish task failed: {result.traceback}"
        
        # Store the story ID before expunging
        story_id = story.id
        
        # 4. Verify story was actually published in database
        db_session.commit()  # Ensure we see committed changes
        db_session.expunge(story)  # Remove from session cache
        updated_story = db_session.query(Story).filter(Story.id == story_id).first()
        assert updated_story is not None
        assert updated_story.is_published is True

    def test_unpublish_story_end_to_end(self, client: TestClient, sample_story_data, db_session: Session):
        """Test complete story unpublishing workflow with real worker."""
        # 1. Create published story
        sample_story_data["is_published"] = True
        story = Story(**sample_story_data)
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        
        assert story.is_published is True
        
        # 2. Submit unpublish task
        response = client.patch(f"/api/v1/stories/{story.id}/unpublish")
        assert response.status_code == 200
        
        task_response = response.json()
        task_id = task_response["task_id"]
        
        # 3. Wait for task completion
        result = AsyncResult(task_id)
        timeout = 30
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        assert result.ready(), f"Unpublish task {task_id} did not complete"
        assert result.successful(), f"Unpublish task failed: {result.traceback}"
        
        # Store the story ID before expunging
        story_id = story.id
        
        # 4. Verify story was actually unpublished in database
        db_session.commit()  # Ensure we see committed changes
        db_session.expunge(story)  # Remove from session cache
        updated_story = db_session.query(Story).filter(Story.id == story_id).first()
        assert updated_story is not None
        assert updated_story.is_published is False

    def test_create_story_with_validation_error(self, client: TestClient):
        """Test that validation errors are handled before task submission."""
        invalid_data = {"title": "", "content": "Test", "author": "Test"}
        
        response = client.post("/api/v1/stories/", json=invalid_data)
        
        # Should fail validation before reaching Celery
        assert response.status_code == 422
        
        # Should not return TaskResponse
        error_response = response.json()
        assert "task_id" not in error_response
        assert "detail" in error_response

    def test_update_nonexistent_story(self, client: TestClient):
        """Test updating a story that doesn't exist."""
        update_data = {"title": "Updated Title"}
        
        # Use no_retry parameter to speed up test
        response = client.put("/api/v1/stories/999999?no_retry=true", json=update_data)
        assert response.status_code == 200  # Task is submitted
        
        task_response = response.json()
        task_id = task_response["task_id"]
        
        # Wait for task completion - it should fail
        result = AsyncResult(task_id)
        timeout = 30
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        assert result.ready(), f"Task {task_id} did not complete"
        # Task should fail because story doesn't exist
        assert result.failed(), "Expected task to fail for nonexistent story"

    def test_delete_nonexistent_story(self, client: TestClient):
        """Test deleting a story that doesn't exist."""
        # Use no_retry parameter to speed up test
        response = client.delete("/api/v1/stories/999999?no_retry=true")
        assert response.status_code == 200  # Task is submitted
        
        task_response = response.json()
        task_id = task_response["task_id"]
        
        # Wait for task completion - it should fail
        result = AsyncResult(task_id)
        timeout = 30
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        assert result.ready(), f"Task {task_id} did not complete"
        # Task should fail because story doesn't exist
        assert result.failed(), "Expected task to fail for nonexistent story"

    def test_concurrent_story_operations(self, client: TestClient, sample_stories_data, db_session: Session):
        """Test multiple concurrent story operations."""
        task_ids = []
        
        # Submit multiple story creation tasks
        for story_data in sample_stories_data:
            response = client.post("/api/v1/stories/", json=story_data)
            assert response.status_code == 200
            task_response = response.json()
            task_ids.append(task_response["task_id"])
        
        # Wait for all tasks to complete
        results = []
        timeout = 45  # Longer timeout for multiple tasks
        
        for task_id in task_ids:
            result = AsyncResult(task_id)
            start_time = time.time()
            while not result.ready() and (time.time() - start_time) < timeout:
                time.sleep(0.5)
            
            assert result.ready(), f"Task {task_id} did not complete"
            assert result.successful(), f"Task {task_id} failed: {result.traceback}"
            results.append(result.get(timeout=5))
        
        # Verify all stories were created
        assert len(results) == len(sample_stories_data)
        
        # Verify all stories exist in database
        db_session.commit()  # Ensure we see committed changes
        created_count = db_session.query(Story).count()
        assert created_count >= len(sample_stories_data)
        
        # Verify each story has correct data
        for i, result in enumerate(results):
            story_id = result["id"]
            story = db_session.query(Story).filter(Story.id == story_id).first()
            assert story is not None
            assert story.title == sample_stories_data[i]["title"]
            assert story.author == sample_stories_data[i]["author"]
