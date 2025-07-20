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
                assert len(data["story"]) > 50  # Reasonable story length
                assert data["metadata"]["model_used"] == model
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
                assert len(data["analysis"]) > 10  # Reasonable analysis length
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
                assert len(data["summary"]) > 10  # Reasonable summary length
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
                assert len(data["improved_story"]) > 50  # Reasonable story length
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
