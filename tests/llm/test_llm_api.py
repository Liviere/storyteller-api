"""
API tests for LLM endpoints using mocks.

This module contains fast API tests that use mocked LLM services.
These tests verify API contract, request validation, and response formatting
without making actual calls to LLM services.

For integration tests with real LLM services, see test_integration.py.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.routers.llm import get_llm_service_dependency
import json


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


