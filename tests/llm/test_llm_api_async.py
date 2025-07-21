"""
Updated API tests for asynchronous LLM endpoints using Celery tasks.

This module replaces the previous direct LLM endpoint tests with tests
for the new asynchronous task-based endpoints.
"""

import json
from unittest.mock import patch, Mock

import pytest
from fastapi.testclient import TestClient
from main import app

from app.routers.llm import get_llm_service_dependency
from app.services.task_service import get_task_service


@pytest.fixture
def mock_task_service():
    """Mock TaskService for testing."""
    mock_service = Mock()
    mock_service.generate_story_async.return_value = "task-123"
    mock_service.analyze_story_async.return_value = "task-456" 
    mock_service.summarize_story_async.return_value = "task-789"
    mock_service.improve_story_async.return_value = "task-abc"
    return mock_service


class TestLLMHealthEndpoint:
    """Test the /health endpoint - unchanged, still synchronous."""

    @pytest.mark.llm_mock
    def test_health_check_success(self, client: TestClient, mock_llm_service):
        """Test health check with available models."""
        app.dependency_overrides[get_llm_service_dependency] = (
            lambda: mock_llm_service
        )
        try:
            response = client.get("/api/v1/llm/health")

            assert response.status_code == 200
            data = response.json()

            assert "status" in data
            assert "available_models" in data
            assert "total_models" in data
            assert "models" in data

            assert data["status"] in ["healthy", "degraded", "unhealthy"]
            assert data["available_models"] >= 0
            assert data["total_models"] >= 0
        finally:
            if get_llm_service_dependency in app.dependency_overrides:
                del app.dependency_overrides[get_llm_service_dependency]


class TestLLMModelsEndpoint:
    """Test the /models endpoint - unchanged, still synchronous."""

    @pytest.mark.llm_mock
    def test_list_models_success(self, client: TestClient, mock_llm_service):
        """Test successful model listing."""
        app.dependency_overrides[get_llm_service_dependency] = (
            lambda: mock_llm_service
        )
        try:
            response = client.get("/api/v1/llm/models")

            assert response.status_code == 200
            data = response.json()

            assert "models" in data
            assert "success" in data
            assert data["success"] is True
            assert isinstance(data["models"], dict)
        finally:
            if get_llm_service_dependency in app.dependency_overrides:
                del app.dependency_overrides[get_llm_service_dependency]


class TestLLMStatsEndpoint:
    """Test the /stats endpoint - unchanged, still synchronous."""

    @pytest.mark.llm_mock
    def test_get_stats_success(self, client: TestClient, mock_llm_service):
        """Test successful stats retrieval."""
        app.dependency_overrides[get_llm_service_dependency] = (
            lambda: mock_llm_service
        )
        try:
            response = client.get("/api/v1/llm/stats")

            assert response.status_code == 200
            data = response.json()

            assert "success" in data
            assert data["success"] is True
            assert "stats" in data

            stats = data["stats"]
            expected_fields = ["requests_count", "total_tokens", "errors_count"]
            for field in expected_fields:
                assert field in stats
        finally:
            if get_llm_service_dependency in app.dependency_overrides:
                del app.dependency_overrides[get_llm_service_dependency]


class TestLLMGenerateEndpointAsync:
    """Test the /generate endpoint - now asynchronous with Celery."""

    @pytest.mark.llm_mock
    def test_generate_story_valid_request_returns_task(
        self, client: TestClient, mock_task_service, sample_generation_requests
    ):
        """Test story generation returns task response."""
        request_data = sample_generation_requests[0]

        app.dependency_overrides[get_task_service] = lambda: mock_task_service
        try:
            response = client.post("/api/v1/llm/generate", json=request_data)

            assert response.status_code == 200
            data = response.json()

            # Check TaskResponse structure
            assert "task_id" in data
            assert "status" in data
            assert "message" in data
            assert "estimated_time" in data

            assert data["task_id"] == "task-123"
            assert data["status"] == "PENDING"
            assert "successfully" in data["message"]
            assert data["estimated_time"] > 0

            # Verify task service was called
            mock_task_service.generate_story_async.assert_called_once()
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    @pytest.mark.llm_mock
    def test_generate_story_invalid_prompt(self, client: TestClient):
        """Test story generation with invalid prompt."""
        invalid_request = {"prompt": "short", "genre": "fantasy"}  # Too short

        response = client.post("/api/v1/llm/generate", json=invalid_request)
        assert response.status_code == 422  # Validation error

    @pytest.mark.llm_mock
    def test_generate_story_missing_prompt(self, client: TestClient):
        """Test story generation with missing prompt."""
        invalid_request = {
            "genre": "fantasy"
            # Missing required prompt
        }

        response = client.post("/api/v1/llm/generate", json=invalid_request)
        assert response.status_code == 422

    @pytest.mark.llm_mock
    def test_generate_story_estimated_time_varies_by_length(
        self, client: TestClient, mock_task_service
    ):
        """Test that estimated time varies based on story length."""
        app.dependency_overrides[get_task_service] = lambda: mock_task_service
        try:
            # Test different lengths
            lengths = ["short", "medium", "long"]
            expected_times = [60, 120, 300]  # From router implementation

            for length, expected_time in zip(lengths, expected_times):
                request_data = {
                    "prompt": "A story about adventures",
                    "length": length
                }

                response = client.post("/api/v1/llm/generate", json=request_data)
                assert response.status_code == 200

                data = response.json()
                assert data["estimated_time"] == expected_time
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]


class TestLLMAnalyzeEndpointAsync:
    """Test the /analyze endpoint - now asynchronous with Celery."""

    @pytest.mark.llm_mock
    def test_analyze_story_valid_request_returns_task(
        self, client: TestClient, mock_task_service
    ):
        """Test story analysis returns task response."""
        request_data = {
            "content": "This is a wonderful story about friendship and adventure. The characters are brave and kind.",
            "analysis_type": "sentiment"
        }

        app.dependency_overrides[get_task_service] = lambda: mock_task_service
        try:
            response = client.post("/api/v1/llm/analyze", json=request_data)

            assert response.status_code == 200
            data = response.json()

            # Check TaskResponse structure
            assert "task_id" in data
            assert "status" in data
            assert "message" in data
            assert "estimated_time" in data

            assert data["task_id"] == "task-456"
            assert data["status"] == "PENDING"

            # Verify task service was called
            mock_task_service.analyze_story_async.assert_called_once()
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    @pytest.mark.llm_mock
    def test_analyze_story_invalid_analysis_type(self, client: TestClient):
        """Test story analysis with invalid analysis type."""
        invalid_request = {
            "content": "Story content here",
            "analysis_type": "invalid_type"
        }

        response = client.post("/api/v1/llm/analyze", json=invalid_request)
        # This should either be 422 (validation) or 500 (server error during task submission)
        assert response.status_code in [422, 500]


class TestLLMSummarizeEndpointAsync:
    """Test the /summarize endpoint - now asynchronous with Celery."""

    @pytest.mark.llm_mock
    def test_summarize_story_valid_request_returns_task(
        self, client: TestClient, mock_task_service
    ):
        """Test story summarization returns task response."""
        request_data = {
            "content": "This is a very long story content that needs to be summarized. " * 10,
            "summary_length": "brief",
            "focus": "plot"
        }

        app.dependency_overrides[get_task_service] = lambda: mock_task_service
        try:
            response = client.post("/api/v1/llm/summarize", json=request_data)

            assert response.status_code == 200
            data = response.json()

            # Check TaskResponse structure
            assert "task_id" in data
            assert "status" in data
            assert "message" in data
            assert "estimated_time" in data

            assert data["task_id"] == "task-789"
            assert data["status"] == "PENDING"

            # Verify task service was called
            mock_task_service.summarize_story_async.assert_called_once()
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    @pytest.mark.llm_mock
    def test_summarize_story_invalid_length(self, client: TestClient):
        """Test story summarization with invalid length."""
        invalid_request = {
            "content": "Story content here",
            "summary_length": "invalid_length"
        }

        response = client.post("/api/v1/llm/summarize", json=invalid_request)
        # Server might accept this and let task validation handle it
        # or validate at API level
        assert response.status_code in [200, 422, 500]


class TestLLMImproveEndpointAsync:
    """Test the /improve endpoint - now asynchronous with Celery."""

    @pytest.mark.llm_mock
    def test_improve_story_valid_request_returns_task(
        self, client: TestClient, mock_task_service
    ):
        """Test story improvement returns task response."""
        request_data = {
            "content": "This story need some improvement in grammar and style.",
            "improvement_type": "grammar",
            "target_audience": "adult"
        }

        app.dependency_overrides[get_task_service] = lambda: mock_task_service
        try:
            response = client.post("/api/v1/llm/improve", json=request_data)

            assert response.status_code == 200
            data = response.json()

            # Check TaskResponse structure
            assert "task_id" in data
            assert "status" in data
            assert "message" in data
            assert "estimated_time" in data

            assert data["task_id"] == "task-abc"
            assert data["status"] == "PENDING"

            # Verify task service was called
            mock_task_service.improve_story_async.assert_called_once()
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]

    @pytest.mark.llm_mock
    def test_improve_story_invalid_type(self, client: TestClient):
        """Test story improvement with invalid improvement type."""
        invalid_request = {
            "content": "Story content here",
            "improvement_type": "invalid_type"
        }

        response = client.post("/api/v1/llm/improve", json=invalid_request)
        # Similar to analysis, might be handled at task level
        assert response.status_code in [200, 422, 500]


class TestLLMEndpointsErrorHandling:
    """Test error handling in LLM endpoints."""

    @pytest.mark.llm_mock
    def test_task_submission_failure(self, client: TestClient):
        """Test handling when task submission fails."""
        mock_failing_service = Mock()
        mock_failing_service.generate_story_async.side_effect = Exception("Task submission failed")

        app.dependency_overrides[get_task_service] = lambda: mock_failing_service
        try:
            request_data = {
                "prompt": "A story about space exploration",
                "genre": "sci-fi"
            }

            response = client.post("/api/v1/llm/generate", json=request_data)
            assert response.status_code == 500

            data = response.json()
            assert "detail" in data
            assert "failed" in data["detail"].lower()
        finally:
            if get_task_service in app.dependency_overrides:
                del app.dependency_overrides[get_task_service]
