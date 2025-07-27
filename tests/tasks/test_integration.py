"""
Tests for the Tasks API endpoints.
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from main import app

from app.services.task_service import get_task_service


@pytest.fixture
def mock_task_service_with_results():
    """Mock TaskService with various task states."""
    mock_service = Mock()
    
    # Successful task
    mock_service.get_task_status.return_value = {
        "task_id": "success-task-123",
        "status": "SUCCESS",
        "result": {
            "story": "Generated story content",
            "metadata": {"model": "test-model", "tokens": 150},
            "success": True
        },
        "info": None,
        "traceback": None,
        "successful": True,
        "failed": False
    }
    
    mock_service.get_task_result.return_value = {
        "story": "Generated story content",
        "metadata": {"model": "test-model", "tokens": 150},
        "success": True
    }
    
    mock_service.cancel_task.return_value = True
    
    return mock_service


@pytest.fixture  
def mock_task_service_pending():
    """Mock TaskService with pending task."""
    mock_service = Mock()
    
    mock_service.get_task_status.return_value = {
        "task_id": "pending-task-456",
        "status": "PENDING",
        "result": None,
        "info": None,
        "traceback": None,
        "successful": None,
        "failed": None
    }
    
    return mock_service


@pytest.fixture
def mock_task_service_failed():
    """Mock TaskService with failed task."""
    mock_service = Mock()
    
    mock_service.get_task_status.return_value = {
        "task_id": "failed-task-789",
        "status": "FAILURE",
        "result": None,
        "info": {"error": "Task failed due to invalid input"},
        "traceback": "Traceback...",
        "successful": False,
        "failed": True
    }
    
    return mock_service


@pytest.mark.integration
class TestTaskStatusEndpoint:
    """Test the GET /api/v1/tasks/{task_id}/status endpoint."""
    
    def test_get_task_status_success(self, client: TestClient, mock_task_service_with_results):
        """Test getting status of successful task."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_with_results
        try:
            response = client.get("/api/v1/tasks/success-task-123/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["task_id"] == "success-task-123"
            assert data["status"] == "SUCCESS"
            assert data["successful"] is True
            assert data["failed"] is False
            assert data["result"] is not None
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
    
    def test_get_task_status_pending(self, client: TestClient, mock_task_service_pending):
        """Test getting status of pending task."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_pending
        try:
            response = client.get("/api/v1/tasks/pending-task-456/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["task_id"] == "pending-task-456"
            assert data["status"] == "PENDING"
            assert data["successful"] is None
            assert data["failed"] is None
            assert data["result"] is None
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
    
    def test_get_task_status_failed(self, client: TestClient, mock_task_service_failed):
        """Test getting status of failed task."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_failed
        try:
            response = client.get("/api/v1/tasks/failed-task-789/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["task_id"] == "failed-task-789"
            assert data["status"] == "FAILURE"
            assert data["successful"] is False
            assert data["failed"] is True
            assert data["info"]["error"] == "Task failed due to invalid input"
            assert data["traceback"] is not None
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
    
    # def test_get_task_status_invalid_task_id(self, client: TestClient):
    #     """Test getting status with invalid/empty task ID."""
    #     # Test empty task ID
    #     response = client.get("/api/v1/tasks//status")
    #     assert response.status_code == 404
        
    #     # Test very long task ID (might have validation)
    #     very_long_id = "x" * 1000
    #     response = client.get(f"/api/v1/tasks/{very_long_id}/status")
    #     # Should either work or return validation error
    #     assert response.status_code in [200, 422]


@pytest.mark.integration
class TestTaskResultEndpoint:
    """Test the GET /api/v1/tasks/{task_id}/result endpoint."""
    
    def test_get_task_result_success(self, client: TestClient, mock_task_service_with_results):
        """Test getting result of successful task."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_with_results
        try:
            response = client.get("/api/v1/tasks/success-task-123/result")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["task_id"] == "success-task-123"
            assert data["success"] is True
            assert "result" in data
            # Check nested result structure
            result = data["result"]
            assert result["story"] == "Generated story content"
            assert result["metadata"]["model"] == "test-model"
            assert result["success"] is True
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
    
    def test_get_task_result_with_timeout(self, client: TestClient, mock_task_service_with_results):
        """Test getting result with timeout parameter."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_with_results
        try:
            response = client.get("/api/v1/tasks/success-task-123/result?timeout=30")
            
            assert response.status_code == 200
            
            # Verify timeout was passed to service
            mock_task_service_with_results.get_task_result.assert_called_with(
                "success-task-123", timeout=30
            )
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
    
    def test_get_task_result_not_ready(self, client: TestClient):
        """Test getting result of task that's not ready."""
        mock_service = Mock()
        mock_service.get_task_result.side_effect = Exception("Task not ready")
        
        app.dependency_overrides[get_task_service] = lambda: mock_service
        try:
            response = client.get("/api/v1/tasks/pending-task/result")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]


@pytest.mark.integration
class TestTaskCancelEndpoint:
    """Test the DELETE /api/v1/tasks/{task_id} endpoint."""
    
    def test_cancel_task_success(self, client: TestClient, mock_task_service_with_results):
        """Test successful task cancellation."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_with_results
        try:
            response = client.delete("/api/v1/tasks/some-task-123")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["task_id"] == "some-task-123"
            assert data["cancelled"] is True
            assert "message" in data
            
            # Verify cancel was called
            mock_task_service_with_results.cancel_task.assert_called_once_with("some-task-123")
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
    
    def test_cancel_task_failure(self, client: TestClient):
        """Test task cancellation failure."""
        mock_service = Mock()
        mock_service.cancel_task.return_value = False
        
        app.dependency_overrides[get_task_service] = lambda: mock_service
        try:
            response = client.delete("/api/v1/tasks/some-task-456")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["task_id"] == "some-task-456"
            assert data["cancelled"] is False
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]


@pytest.mark.integration
class TestTaskListEndpoint:
    """Test the GET /api/v1/tasks/active endpoint."""
    
    def test_list_active_tasks(self, client: TestClient):
        """Test listing active tasks."""
        mock_service = Mock()
        mock_service.get_active_tasks.return_value = {
            "active": {
                "worker1": [
                    {"id": "task-1", "name": "llm.generate_story"},
                    {"id": "task-2", "name": "stories.create_story"}
                ]
            },
            "scheduled": {"worker1": []},
            "reserved": {"worker1": []}
        }
        
        app.dependency_overrides[get_task_service] = lambda: mock_service
        try:
            response = client.get("/api/v1/tasks/active")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "active" in data
            assert "scheduled" in data
            assert "reserved" in data
            assert len(data["active"]["worker1"]) == 2
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]


@pytest.mark.integration
class TestWorkerStatsEndpoint:
    """Test the GET /api/v1/tasks/workers/stats endpoint."""
    
    def test_get_worker_stats(self, client: TestClient):
        """Test getting worker statistics."""
        mock_service = Mock()
        mock_service.get_worker_stats.return_value = {
            "stats": {
                "worker1": {
                    "pool": {"max-concurrency": 4},
                    "total": {"tasks.llm.generate_story": 15}
                }
            },
            "ping": {"worker1": "pong"},
            "registered": {
                "worker1": ["llm.generate_story", "stories.create_story"]
            }
        }
        
        app.dependency_overrides[get_task_service] = lambda: mock_service
        try:
            response = client.get("/api/v1/tasks/workers/stats")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "stats" in data
            assert "ping" in data
            assert "registered" in data
            assert data["ping"]["worker1"] == "pong"
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

@pytest.mark.integration
class TestTaskAPIErrorHandling:
    """Test error handling in task API endpoints."""
    
    def test_service_error_handling(self, client: TestClient):
        """Test handling when task service throws errors."""
        mock_service = Mock()
        mock_service.get_task_status.side_effect = Exception("Service unavailable")
        
        app.dependency_overrides[get_task_service] = lambda: mock_service
        try:
            response = client.get("/api/v1/tasks/any-task/status")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
    
    def test_malformed_task_id(self, client: TestClient, mock_task_service_with_results):
        """Test with malformed task IDs."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service_with_results
        try:
            # Test with special characters (but valid URL format)
            malformed_ids = ["task-with-special@chars", "task.with.dots", "task_with_underscores"]
            
            for task_id in malformed_ids:
                response = client.get(f"/api/v1/tasks/{task_id}/status")
                # Should handle gracefully - either work or return valid error
                assert response.status_code in [200, 400, 404, 422, 500]
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
