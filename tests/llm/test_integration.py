"""
Integration tests for LLM API endpoints.
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from main import app
from app.routers.llm import get_llm_service_dependency


@pytest.mark.integration
class TestLLMHealthIntegration:
    """Integration tests for the /health endpoint."""

    
    def test_health_check_real_service(
        self, client: TestClient, skip_llm_integration_tests
    ):
        """Test health check with real LLM service."""
        response = client.get("/api/v1/llm/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "models" in data

@pytest.mark.integration
class TestLLMModelsIntegration:
    """Integration tests for the /models endpoint."""

    
    def test_list_models_real_service(self, client: TestClient, skip_llm_integration_tests):
        """Test model listing with real LLM service."""
        response = client.get("/api/v1/llm/models")

        assert response.status_code == 200
        data = response.json()

        assert "models" in data
        assert isinstance(data["models"], dict)

@pytest.mark.integration
class TestLLMGenerationIntegration:
    """Integration tests for story generation."""

    def test_generate_with_testing_models(
        self, client: TestClient, test_models, skip_llm_integration_tests
    ):
        """Test story generation with configured testing models."""
        testing_models = test_models.get("story_generation", [])

        if not testing_models:
            pytest.skip("No testing models configured for story_generation")

        request_data = {
            "prompt": "A short story about a robot learning to love",
            "genre": "science fiction",
            "length": "short",
        }

        for model in testing_models:
            request_data["model_name"] = model
            response = client.post("/api/v1/llm/generate", json=request_data)

            # Should either succeed or fail gracefully
            if response.status_code == 200:
                data = response.json()
                # Async API returns task info instead of direct story
                assert "task_id" in data
                assert "status" in data  
                assert "message" in data
                assert "estimated_time" in data
                assert data["status"] == "PENDING"
            else:
                # If it fails, it should be a known error (e.g., model unavailable)
                assert response.status_code in [400, 500, 503]

@pytest.mark.integration
class TestLLMAnalysisIntegration:
    """Integration tests for story analysis."""

    
    
    def test_analyze_with_testing_models(
        self,
        client: TestClient,
        test_models,
        sample_story_content,
        skip_llm_integration_tests,
    ):
        """Test story analysis with configured testing models."""
        testing_models = test_models.get("analysis", [])

        if not testing_models:
            pytest.skip("No testing models configured for analysis")

        request_data = {"content": sample_story_content, "analysis_type": "sentiment"}

        for model in testing_models:
            request_data["model_name"] = model
            response = client.post("/api/v1/llm/analyze", json=request_data)

            if response.status_code == 200:
                data = response.json()
                # Async API returns task info instead of direct analysis
                assert "task_id" in data
                assert "status" in data
                assert "message" in data
                assert "estimated_time" in data
                assert data["status"] == "PENDING"
            else:
                assert response.status_code in [400, 500, 503]

@pytest.mark.integration
class TestLLMSummarizationIntegration:
    """Integration tests for story summarization."""

    
    
    def test_summarize_with_testing_models(
        self,
        client: TestClient,
        test_models,
        sample_story_content,
        skip_llm_integration_tests,
    ):
        """Test story summarization with configured testing models."""
        testing_models = test_models.get("summarization", [])

        if not testing_models:
            pytest.skip("No testing models configured for summarization")

        request_data = {"content": sample_story_content, "summary_length": "brief"}

        for model in testing_models:
            request_data["model_name"] = model
            response = client.post("/api/v1/llm/summarize", json=request_data)

            if response.status_code == 200:
                data = response.json()
                # Async API returns task info instead of direct summary
                assert "task_id" in data
                assert "status" in data
                assert "message" in data
                assert "estimated_time" in data
                assert data["status"] == "PENDING"
            else:
                assert response.status_code in [400, 500, 503]

@pytest.mark.integration
class TestLLMImprovementIntegration:
    """Integration tests for story improvement."""

    
    
    def test_improve_with_testing_models(
        self,
        client: TestClient,
        test_models,
        sample_story_content,
        skip_llm_integration_tests,
    ):
        """Test story improvement with configured testing models."""
        testing_models = test_models.get("improvement", [])

        if not testing_models:
            pytest.skip("No testing models configured for improvement")

        request_data = {"content": sample_story_content, "improvement_type": "general"}

        for model in testing_models:
            request_data["model_name"] = model
            response = client.post("/api/v1/llm/improve", json=request_data)

            if response.status_code == 200:
                data = response.json()
                # Async API returns task info instead of direct improved story
                assert "task_id" in data
                assert "status" in data
                assert "message" in data
                assert "estimated_time" in data
                assert data["status"] == "PENDING"
            else:
                assert response.status_code in [400, 500, 503]

@pytest.mark.integration
class TestLLMHealthEndpoint:
    """Test the /health endpoint - unchanged, still synchronous."""

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

@pytest.mark.integration
class TestLLMModelsEndpoint:
    """Test the /models endpoint - unchanged, still synchronous."""

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

@pytest.mark.integration
class TestLLMStatsEndpoint:
    """Test the /stats endpoint - unchanged, still synchronous."""

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
