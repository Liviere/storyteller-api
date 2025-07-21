"""
E2E Workflow Tests for Async API

End-to-end tests that verify complete workflows using the new asynchronous API.
These tests simulate real user interactions with task submission and monitoring.
"""

import pytest
import time
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.main import app
from app.services.task_service import get_task_service


class TestAsyncStoryWorkflows:
    """End-to-end workflow tests for async Stories and LLM API."""

    @pytest.fixture
    def mock_task_service_e2e(self):
        """Mock TaskService for E2E testing with realistic responses."""
        mock_service = Mock()
        
        # Mock task submissions
        mock_service.create_story_async.return_value = "e2e-create-123"
        mock_service.update_story_async.return_value = "e2e-update-456"
        mock_service.delete_story_async.return_value = "e2e-delete-789"
        mock_service.patch_story_async.return_value = "e2e-patch-101"
        mock_service.generate_story_async.return_value = "e2e-generate-202"
        mock_service.analyze_story_async.return_value = "e2e-analyze-303"
        
        # Mock worker/active task methods
        mock_service.get_active_tasks.return_value = {
            "active": {"worker1": []},
            "scheduled": {"worker1": []}, 
            "reserved": {"worker1": []}
        }
        
        mock_service.get_worker_stats.return_value = {
            "stats": {"worker1": {"pool": {"max-concurrency": 4}}},
            "ping": {"worker1": {"ok": "pong"}},
            "registered": {"worker1": ["tasks.stories.create", "tasks.llm.generate"]}
        }
        
        # Mock task status and results
        mock_service.get_task_status.return_value = {
            "status": "SUCCESS",
            "result": {
                "id": 1,
                "title": "Created Story",
                "content": "Generated content",
                "author": "Test Author",
                "genre": "Test",
                "is_published": False,
                "created_at": "2025-07-21T10:00:00Z",
                "updated_at": "2025-07-21T10:00:00Z"
            },
            "info": None,
            "traceback": None,
            "successful": True,
            "failed": False
        }
        
        mock_service.get_task_result.return_value = {
            "id": 1,
            "title": "Created Story",
            "content": "Generated content",
            "author": "Test Author",
            "genre": "Test",
            "is_published": False,
            "created_at": "2025-07-21T10:00:00Z",
            "updated_at": "2025-07-21T10:00:00Z"
        }
        
        return mock_service

    def test_async_story_creation_workflow(self, client: TestClient, mock_task_service_e2e):
        """Test complete async story creation workflow."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_e2e
        try:
            # Step 1: Submit story creation task
            story_data = {
                "title": "E2E Test Story",
                "content": "Content for E2E testing",
                "author": "E2E Tester",
                "genre": "Test",
                "is_published": False
            }
            
            create_response = client.post("/api/v1/stories/", json=story_data)
            assert create_response.status_code == status.HTTP_200_OK
            
            task_data = create_response.json()
            assert "task_id" in task_data
            assert task_data["status"] == "PENDING"
            task_id = task_data["task_id"]
            
            # Step 2: Check task status
            status_response = client.get(f"/api/v1/tasks/{task_id}/status")
            assert status_response.status_code == status.HTTP_200_OK
            
            status_data = status_response.json()
            assert status_data["task_id"] == task_id
            assert status_data["status"] == "SUCCESS"
            assert status_data["successful"] is True
            
            # Step 3: Get task result
            result_response = client.get(f"/api/v1/tasks/{task_id}/result")
            assert result_response.status_code == status.HTTP_200_OK
            
            result_data = result_response.json()
            assert result_data["task_id"] == task_id
            assert result_data["success"] is True
            
            # Verify the created story data
            story_result = result_data["result"]
            assert story_result["id"] == 1
            assert "title" in story_result
            assert "created_at" in story_result
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_async_story_update_workflow(self, client: TestClient, mock_task_service_e2e):
        """Test async story update workflow."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_e2e
        try:
            # Setup: Mock updated story result
            mock_task_service_e2e.get_task_result.return_value = {
                "id": 1,
                "title": "Updated Story Title",
                "content": "Updated content",
                "author": "Test Author",
                "genre": "Test",
                "is_published": False,
                "created_at": "2025-07-21T10:00:00Z",
                "updated_at": "2025-07-21T10:05:00Z"
            }
            
            # Step 1: Submit update task
            update_data = {
                "title": "Updated Story Title",
                "content": "Updated content"
            }
            
            update_response = client.put("/api/v1/stories/1", json=update_data)
            assert update_response.status_code == status.HTTP_200_OK
            
            task_data = update_response.json()
            task_id = task_data["task_id"]
            
            # Step 2: Get update result
            result_response = client.get(f"/api/v1/tasks/{task_id}/result")
            assert result_response.status_code == status.HTTP_200_OK
            
            result_data = result_response.json()
            story_result = result_data["result"]
            
            # Verify the update was applied
            assert story_result["title"] == update_data["title"]
            assert story_result["content"] == update_data["content"]
            assert story_result["updated_at"] != story_result["created_at"]
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_async_story_publish_workflow(self, client: TestClient, mock_task_service_e2e):
        """Test async story publish workflow."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_e2e
        try:
            # Setup: Mock published story result
            mock_task_service_e2e.get_task_result.return_value = {
                "id": 1,
                "title": "Story to Publish",
                "content": "Content",
                "author": "Test Author",
                "genre": "Test",
                "is_published": True,  # Published!
                "created_at": "2025-07-21T10:00:00Z",
                "updated_at": "2025-07-21T10:10:00Z"
            }
            
            # Step 1: Submit publish task
            publish_response = client.patch("/api/v1/stories/1/publish")
            assert publish_response.status_code == status.HTTP_200_OK
            
            task_data = publish_response.json()
            task_id = task_data["task_id"]
            assert "publish" in task_data["message"].lower()
            
            # Step 2: Get publish result
            result_response = client.get(f"/api/v1/tasks/{task_id}/result")
            assert result_response.status_code == status.HTTP_200_OK
            
            result_data = result_response.json()
            story_result = result_data["result"]
            
            # Verify the story was published
            assert story_result["is_published"] is True
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_llm_generation_workflow(self, client: TestClient, mock_task_service_e2e):
        """Test LLM story generation workflow."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_e2e
        try:
            # Setup: Mock LLM generation result
            mock_task_service_e2e.get_task_result.return_value = {
                "story": "Once upon a time, in a magical land...",
                "metadata": {
                    "model": "test-model",
                    "tokens": 150,
                    "generation_time": 2.5
                },
                "success": True
            }
            
            # Step 1: Submit LLM generation task
            llm_request = {
                "prompt": "Write a fantasy story about a brave knight",
                "max_length": 500,
                "model": "test-model"
            }
            
            generate_response = client.post("/api/v1/llm/generate", json=llm_request)
            assert generate_response.status_code == status.HTTP_200_OK
            
            task_data = generate_response.json()
            task_id = task_data["task_id"]
            assert task_data["status"] == "PENDING"
            
            # Step 2: Get generation result
            result_response = client.get(f"/api/v1/tasks/{task_id}/result")
            assert result_response.status_code == status.HTTP_200_OK
            
            result_data = result_response.json()
            llm_result = result_data["result"]
            
            # Verify the generated content
            assert "story" in llm_result
            assert llm_result["story"].startswith("Once upon a time")
            assert llm_result["success"] is True
            assert "metadata" in llm_result
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_complete_async_workflow_with_llm(self, client: TestClient, mock_task_service_e2e):
        """Test complete workflow: LLM generation -> Story creation -> Operations."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_e2e
        try:
            # Mock different results for different calls
            def mock_get_result(task_id, timeout=None):
                if "generate" in task_id:
                    return {
                        "story": "Generated story content from LLM",
                        "metadata": {"model": "test-model", "tokens": 100},
                        "success": True
                    }
                elif "create" in task_id:
                    return {
                        "id": 1,
                        "title": "Generated Story",
                        "content": "Generated story content from LLM",
                        "author": "AI Assistant",
                        "genre": "Generated",
                        "is_published": False,
                        "created_at": "2025-07-21T10:00:00Z"
                    }
                elif "analyze" in task_id:
                    return {
                        "sentiment": "positive",
                        "genre_classification": "fantasy",
                        "themes": ["adventure", "friendship"],
                        "success": True
                    }
                
            mock_task_service_e2e.get_task_result.side_effect = mock_get_result
            
            # Step 1: Generate story with LLM
            llm_request = {
                "prompt": "Write a story about friendship",
                "max_length": 300
            }
            
            generate_response = client.post("/api/v1/llm/generate", json=llm_request)
            assert generate_response.status_code == status.HTTP_200_OK
            generate_task_id = generate_response.json()["task_id"]
            
            # Get generated content
            gen_result_response = client.get(f"/api/v1/tasks/{generate_task_id}/result")
            generated_content = gen_result_response.json()["result"]["story"]
            
            # Step 2: Create story from generated content
            story_data = {
                "title": "Generated Story",
                "content": generated_content,
                "author": "AI Assistant",
                "genre": "Generated"
            }
            
            create_response = client.post("/api/v1/stories/", json=story_data)
            assert create_response.status_code == status.HTTP_200_OK
            create_task_id = create_response.json()["task_id"]
            
            # Get created story
            create_result_response = client.get(f"/api/v1/tasks/{create_task_id}/result")
            created_story = create_result_response.json()["result"]
            
            # Step 3: Analyze the created story
            analyze_request = {
                "content": "This is a much longer content for comprehensive analysis that meets the minimum length requirement of 50 characters for the LLM analyze endpoint to process properly.",
                "analysis_type": "full"  # Changed from "comprehensive" to "full"
            }
            
            analyze_response = client.post("/api/v1/llm/analyze", json=analyze_request)
            assert analyze_response.status_code == status.HTTP_200_OK
            analyze_task_id = analyze_response.json()["task_id"]
            
            # Get analysis result
            analysis_result_response = client.get(f"/api/v1/tasks/{analyze_task_id}/result")
            analysis = analysis_result_response.json()["result"]
            
            # Verify complete workflow
            assert created_story["content"] == generated_content
            assert analysis["sentiment"] == "positive"
            assert analysis["success"] is True
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_task_monitoring_workflow(self, client: TestClient, mock_task_service_e2e):
        """Test task monitoring and status checking workflow."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_e2e
        try:
            # Mock different task states over time
            def mock_get_status(task_id):
                # Simulate task progression
                return {
                    "status": "SUCCESS",
                    "result": {"message": "Task completed"},
                    "info": {"progress": "100%"},
                    "traceback": None,
                    "successful": True,
                    "failed": False
                }
                
            mock_task_service_e2e.get_task_status.side_effect = mock_get_status
            
            # Step 1: Submit a task
            story_data = {"title": "Test", "content": "Content", "author": "Author"}
            response = client.post("/api/v1/stories/", json=story_data)
            task_id = response.json()["task_id"]
            
            # Step 2: Monitor task status
            status_response = client.get(f"/api/v1/tasks/{task_id}/status")
            assert status_response.status_code == status.HTTP_200_OK
            
            status_data = status_response.json()
            assert status_data["status"] == "SUCCESS"
            assert status_data["successful"] is True
            
            # Step 3: Check active tasks
            active_response = client.get("/api/v1/tasks/active")
            assert active_response.status_code == status.HTTP_200_OK
            
            # Step 4: Check worker stats
            stats_response = client.get("/api/v1/tasks/workers/stats")
            assert stats_response.status_code == status.HTTP_200_OK
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]


class TestErrorHandlingWorkflows:
    """Test error handling in async workflows."""
    
    def test_task_failure_workflow(self, client: TestClient):
        """Test handling of failed tasks."""
        # Mock a failing TaskService
        mock_service = Mock()
        mock_service.create_story_async.side_effect = Exception("Storage error")
        
        app.dependency_overrides[get_task_service] = lambda: mock_service
        try:
            story_data = {"title": "Test", "content": "Content", "author": "Author"}
            response = client.post("/api/v1/stories/", json=story_data)
            
            # Should return 500 error for task submission failure
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            error_data = response.json()
            assert "Failed to submit" in error_data["detail"]
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    def test_nonexistent_task_workflow(self, client: TestClient):
        """Test workflow with non-existent task IDs."""
        # Mock service that can handle nonexistent tasks appropriately
        mock_service = Mock()
        
        # Configure mock to simulate nonexistent task behavior
        mock_service.get_task_status.side_effect = Exception("Task not found")
        
        app.dependency_overrides[get_task_service] = lambda: mock_service
        try:
            # Test checking status of non-existent task
            response = client.get("/api/v1/tasks/nonexistent-task-123/status")
            
            # Should return 500 due to the exception
            assert response.status_code == 500
            assert "Task not found" in response.json()["detail"]
            
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
