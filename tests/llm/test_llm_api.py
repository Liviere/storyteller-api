"""
Tests for LLM API endpoints.

This module contains tests for all LLM-related API endpoints including:
- Story generation
- Story analysis  
- Story summarization
- Story improvement
- Model listing
- Health checks

Tests are organized into mock tests (fast) and integration tests (slow).
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.routers.llm import get_llm_service_dependency
import json

from app.llm.services import get_llm_service
from tests.llm.conftest_llm import skip_integration_tests


class TestLLMHealthEndpoint:
    """Test the /health endpoint."""
    
    @pytest.mark.llm_mock
    def test_health_check_success(self, client: TestClient, mock_llm_service):
        """Test health check with available models."""
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
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
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]
    
    @pytest.mark.llm_mock
    def test_health_check_with_no_available_models(self, client: TestClient):
        """Test health check response when system reports models but none are available."""
        # This test verifies the response format when models exist but are unavailable
        # We'll use the real service but expect it to handle gracefully
        response = client.get("/api/v1/llm/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert "available_models" in data
        assert "total_models" in data
        assert "models" in data
        
        # Status should be one of the valid states
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        
        # Models count should be non-negative
        assert data["available_models"] >= 0
        assert data["total_models"] >= 0
        assert isinstance(data["models"], dict)
    
    @pytest.mark.llm_integration
    def test_health_check_real_service(self, client: TestClient, skip_integration_tests):
        """Test health check with real LLM service."""
        response = client.get("/api/v1/llm/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "models" in data


class TestLLMModelsEndpoint:
    """Test the /models endpoint."""
    
    @pytest.mark.llm_mock
    def test_list_models_success(self, client: TestClient, mock_llm_service):
        """Test successful model listing."""
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            response = client.get("/api/v1/llm/models")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "models" in data
            assert "success" in data
            assert data["success"] is True
            assert isinstance(data["models"], dict)
        finally:
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]
    
    @pytest.mark.llm_integration
    def test_list_models_real_service(self, client: TestClient, skip_integration_tests):
        """Test model listing with real service."""
        response = client.get("/api/v1/llm/models")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert isinstance(data["models"], dict)


class TestLLMStatsEndpoint:
    """Test the /stats endpoint."""
    
    @pytest.mark.llm_mock
    def test_get_stats_success(self, client: TestClient, mock_llm_service):
        """Test successful stats retrieval."""
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            response = client.get("/api/v1/llm/stats")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "stats" in data
            assert "success" in data
            assert data["success"] is True
            assert isinstance(data["stats"], dict)
            
            # Check for expected stats fields
            stats = data["stats"]
            expected_fields = ["requests_count", "total_tokens", "errors_count"]
            for field in expected_fields:
                assert field in stats
        finally:
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]


class TestLLMGenerateEndpoint:
    """Test the /generate endpoint."""
    
    @pytest.mark.llm_mock
    def test_generate_story_valid_request(self, client: TestClient, mock_llm_service, sample_generation_requests):
        """Test story generation with valid request."""
        request_data = sample_generation_requests[0]
        
        # Override the dependency to return our mock
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            response = client.post("/api/v1/llm/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "story" in data
            assert "metadata" in data
            assert "success" in data
            assert data["success"] is True
            assert len(data["story"]) > 0
            
            # Verify that mock response is used
            assert data["story"] == "Once upon a time, in a land far away..."
            assert data["metadata"]["model"] == "test-model"
            assert data["metadata"]["tokens_used"] == 150
            
            # Verify mock was called
            mock_llm_service.generate_story.assert_called_once()
        finally:
            # Clean up the override
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]
    
    @pytest.mark.llm_mock
    def test_generate_story_invalid_prompt(self, client: TestClient, mock_llm_service):
        """Test story generation with invalid prompt."""
        invalid_request = {
            "prompt": "short",  # Too short
            "genre": "fantasy"
        }
        
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
    def test_generate_story_all_samples(self, client: TestClient, mock_llm_service, sample_generation_requests):
        """Test story generation with all sample requests."""
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            for i, request in enumerate(sample_generation_requests):
                response = client.post("/api/v1/llm/generate", json=request)
                
                assert response.status_code == 200, f"Request {i} failed"
                data = response.json()
                assert data["success"] is True, f"Request {i} not successful"
                
                # Verify that mock response is used
                assert data["story"] == "Once upon a time, in a land far away...", f"Request {i} not using mock story"
                assert data["metadata"]["model"] == "test-model", f"Request {i} not using mock model"
            
            # Verify mock was called for each request
            assert mock_llm_service.generate_story.call_count == len(sample_generation_requests)
        finally:
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]


class TestLLMAnalyzeEndpoint:
    """Test the /analyze endpoint."""
    
    @pytest.mark.llm_mock
    def test_analyze_story_valid_request(self, client: TestClient, mock_llm_service, sample_analysis_requests):
        """Test story analysis with valid request."""
        request_data = sample_analysis_requests[0]
        
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            response = client.post("/api/v1/llm/analyze", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "analysis" in data
            assert "analysis_type" in data
            assert "metadata" in data
            assert "success" in data
            assert data["success"] is True
            
            # Verify that mock response is used
            assert data["analysis"] == "This is a fantasy story with positive sentiment."
            assert data["metadata"]["model"] == "test-model"
            assert data["metadata"]["confidence"] == 0.85
            
            # Verify mock was called
            mock_llm_service.analyze_story.assert_called_once()
        finally:
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]
    
    @pytest.mark.llm_mock
    def test_analyze_story_invalid_analysis_type(self, client: TestClient, mock_llm_service, sample_story_content):
        """Test story analysis with invalid analysis type."""
        invalid_request = {
            "content": sample_story_content,
            "analysis_type": "invalid_type"
        }
        
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            response = client.post("/api/v1/llm/analyze", json=invalid_request)
            
            assert response.status_code == 400
        finally:
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]


class TestLLMSummarizeEndpoint:
    """Test the /summarize endpoint."""
    
    @pytest.mark.llm_mock
    def test_summarize_story_valid_request(self, client: TestClient, mock_llm_service, sample_summary_requests):
        """Test story summarization with valid request."""
        request_data = sample_summary_requests[0]
        
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            response = client.post("/api/v1/llm/summarize", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "summary" in data
            assert "metadata" in data
            assert "success" in data
            assert data["success"] is True
            
            # Verify that mock response is used
            assert data["summary"] == "A brief summary of the story content."
            assert data["metadata"]["model"] == "test-model"
            assert data["metadata"]["original_length"] == 500
            
            # Verify mock was called
            mock_llm_service.summarize_story.assert_called_once()
        finally:
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]
    
    @pytest.mark.llm_mock
    def test_summarize_story_invalid_length(self, client: TestClient, mock_llm_service, sample_story_content):
        """Test story summarization with invalid length."""
        invalid_request = {
            "content": sample_story_content,
            "summary_length": "invalid_length"
        }
        
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            response = client.post("/api/v1/llm/summarize", json=invalid_request)
            
            assert response.status_code == 400
        finally:
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]


class TestLLMImproveEndpoint:
    """Test the /improve endpoint."""
    
    @pytest.mark.llm_mock
    def test_improve_story_valid_request(self, client: TestClient, mock_llm_service, sample_improvement_requests):
        """Test story improvement with valid request."""
        request_data = sample_improvement_requests[0]
        
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            response = client.post("/api/v1/llm/improve", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "improved_story" in data
            assert "original_story" in data
            assert "metadata" in data
            assert "success" in data
            assert data["success"] is True
            
            # Verify that mock response is used
            assert data["improved_story"] == "An improved version of the story."
            assert data["original_story"] == "Original story content."
            assert data["metadata"]["model"] == "test-model"
            assert data["metadata"]["improvement_type"] == "general"
            
            # Verify mock was called
            mock_llm_service.improve_story.assert_called_once()
        finally:
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]
    
    @pytest.mark.llm_mock
    def test_improve_story_invalid_type(self, client: TestClient, mock_llm_service, sample_story_content):
        """Test story improvement with invalid improvement type."""
        invalid_request = {
            "content": sample_story_content,
            "improvement_type": "invalid_type"
        }
        
        client.app.dependency_overrides[get_llm_service_dependency] = lambda: mock_llm_service
        try:
            response = client.post("/api/v1/llm/improve", json=invalid_request)
            
            assert response.status_code == 400
        finally:
            if get_llm_service_dependency in client.app.dependency_overrides:
                del client.app.dependency_overrides[get_llm_service_dependency]


# Integration tests with real models (slow)
class TestLLMIntegrationTests:
    """Integration tests with real LLM models."""
    
    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_generate_with_testing_models(self, client: TestClient, integration_test_models, skip_integration_tests):
        """Test story generation with configured testing models."""
        testing_models = integration_test_models.get("story_generation", [])
        
        if not testing_models:
            pytest.skip("No testing models configured for story_generation")
        
        request_data = {
            "prompt": "A short story about a robot learning to love",
            "genre": "science fiction",
            "length": "short"
        }
        
        for model in testing_models:
            request_data["model_name"] = model
            response = client.post("/api/v1/llm/generate", json=request_data)
            
            # Should either succeed or fail gracefully
            if response.status_code == 200:
                data = response.json()
                assert len(data["story"]) > 50  # Reasonable story length
                assert data["metadata"]["model_used"] == model
            else:
                # If it fails, it should be a known error (e.g., model unavailable)
                assert response.status_code in [400, 500, 503]
    
    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_analyze_with_testing_models(self, client: TestClient, integration_test_models, sample_story_content, skip_integration_tests):
        """Test story analysis with configured testing models."""
        testing_models = integration_test_models.get("analysis", [])
        
        if not testing_models:
            pytest.skip("No testing models configured for analysis")
        
        request_data = {
            "content": sample_story_content,
            "analysis_type": "sentiment"
        }
        
        for model in testing_models:
            request_data["model_name"] = model
            response = client.post("/api/v1/llm/analyze", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                assert len(data["analysis"]) > 10  # Reasonable analysis length
            else:
                assert response.status_code in [400, 500, 503]
    
    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_summarize_with_testing_models(self, client: TestClient, integration_test_models, sample_story_content, skip_integration_tests):
        """Test story summarization with configured testing models."""
        testing_models = integration_test_models.get("summarization", [])
        
        if not testing_models:
            pytest.skip("No testing models configured for summarization")
        
        request_data = {
            "content": sample_story_content,
            "summary_length": "brief"
        }
        
        for model in testing_models:
            request_data["model_name"] = model
            response = client.post("/api/v1/llm/summarize", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                assert len(data["summary"]) > 20  # Reasonable summary length
                # Summary should contain relevant content
                assert "Luna" in data["summary"] or "forest" in data["summary"] or "fountain" in data["summary"]
            else:
                assert response.status_code in [400, 500, 503]
    
    @pytest.mark.llm_integration
    @pytest.mark.slow 
    def test_improve_with_testing_models(self, client: TestClient, integration_test_models, skip_integration_tests):
        """Test story improvement with configured testing models."""
        testing_models = integration_test_models.get("improvement", [])
        
        if not testing_models:
            pytest.skip("No testing models configured for improvement")
        
        # Use a simple story with obvious grammar issues
        story_to_improve = "this story have bad grammar and need fix. it not good writing style."
        
        request_data = {
            "content": story_to_improve,
            "improvement_type": "grammar"
        }
        
        for model in testing_models:
            request_data["model_name"] = model
            response = client.post("/api/v1/llm/improve", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                assert len(data["improved_story"]) > 0
                assert data["original_story"] == story_to_improve
                # Improved story should be different from original
                assert data["improved_story"] != story_to_improve
            else:
                assert response.status_code in [400, 500, 503]
