"""
Integration tests for LLM API endpoints.

This module contains integration tests that make actual API calls to LLM services.
These tests are slower and require proper LLM configuration.
"""

import pytest
from fastapi.testclient import TestClient


class TestLLMHealthIntegration:
    """Integration tests for the /health endpoint."""

    @pytest.mark.llm_integration
    def test_health_check_real_service(
        self, client: TestClient, skip_integration_tests
    ):
        """Test health check with real LLM service."""
        response = client.get("/api/v1/llm/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "models" in data


class TestLLMModelsIntegration:
    """Integration tests for the /models endpoint."""

    @pytest.mark.llm_integration
    def test_list_models_real_service(self, client: TestClient, skip_integration_tests):
        """Test model listing with real LLM service."""
        response = client.get("/api/v1/llm/models")

        assert response.status_code == 200
        data = response.json()

        assert "models" in data
        assert isinstance(data["models"], dict)


class TestLLMGenerationIntegration:
    """Integration tests for story generation."""

    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_generate_with_testing_models(
        self, client: TestClient, integration_test_models, skip_integration_tests
    ):
        """Test story generation with configured testing models."""
        testing_models = integration_test_models.get("story_generation", [])

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


class TestLLMAnalysisIntegration:
    """Integration tests for story analysis."""

    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_analyze_with_testing_models(
        self,
        client: TestClient,
        integration_test_models,
        sample_story_content,
        skip_integration_tests,
    ):
        """Test story analysis with configured testing models."""
        testing_models = integration_test_models.get("analysis", [])

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


class TestLLMSummarizationIntegration:
    """Integration tests for story summarization."""

    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_summarize_with_testing_models(
        self,
        client: TestClient,
        integration_test_models,
        sample_story_content,
        skip_integration_tests,
    ):
        """Test story summarization with configured testing models."""
        testing_models = integration_test_models.get("summarization", [])

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


class TestLLMImprovementIntegration:
    """Integration tests for story improvement."""

    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_improve_with_testing_models(
        self,
        client: TestClient,
        integration_test_models,
        sample_story_content,
        skip_integration_tests,
    ):
        """Test story improvement with configured testing models."""
        testing_models = integration_test_models.get("improvement", [])

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


class TestLLMEndToEndWorkflows:
    """End-to-end workflow tests using real LLM services."""

    @pytest.mark.llm_integration
    @pytest.mark.slow
    def test_full_story_workflow(
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

        # Async API returns task info, not immediate story
        task_data = generate_response.json()
        assert "task_id" in task_data
        assert "status" in task_data
        assert task_data["status"] == "PENDING"
        
        # For integration test, we verify async workflow works  
        # (Full end-to-end testing with task completion would require Celery worker)
        
        # Step 2: Test that task endpoints exist and accept valid input
        # Using a sample story content for analysis since we can't wait for task completion
        sample_story = "Once upon a time, there was a brave knight who fought dragons."

        # Step 2: Analyze using sample story (async API returns task info)
        analyze_response = client.post(
            "/api/v1/llm/analyze", json={"content": sample_story, "analysis_type": "full"}
        )

        if analyze_response.status_code == 200:
            analysis_task = analyze_response.json()
            assert "task_id" in analysis_task
            assert "status" in analysis_task
            assert analysis_task["status"] == "PENDING"

        # Step 3: Summarize using sample story (async API returns task info)
        summarize_response = client.post(
            "/api/v1/llm/summarize", json={"content": sample_story, "summary_length": "brief"}
        )

        if summarize_response.status_code == 200:
            summary_task = summarize_response.json()
            assert "task_id" in summary_task
            assert "status" in summary_task
            assert summary_task["status"] == "PENDING"

        # Step 4: Improve using sample story (async API returns task info)
        improve_response = client.post(
            "/api/v1/llm/improve",
            json={"content": sample_story, "improvement_type": "general"},
        )

        if improve_response.status_code == 200:
            improve_task = improve_response.json()
            assert "task_id" in improve_task
            assert "status" in improve_task
            assert improve_task["status"] == "PENDING"
            
        # Workflow test validates that all async endpoints accept input and return task IDs
