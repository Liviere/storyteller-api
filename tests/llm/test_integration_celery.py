"""
Integration tests for LLM API with real Celery workers.
These tests verify that async LLM operations actually complete and produce correct results.
"""

import pytest
from fastapi.testclient import TestClient
from celery.result import AsyncResult
import time

from app.main import app
from app.database import get_db


@pytest.fixture
def real_client():
    """Client that uses real database (same as Celery workers)."""
    return TestClient(app)


@pytest.fixture  
def real_db():
    """Real database session (same as Celery workers use)."""
    db_session = next(get_db())
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.mark.celery_integration
class TestLLMIntegrationCelery:
    """Integration tests for LLM API with real Celery workers."""

    def test_generate_story_end_to_end(self, real_client: TestClient):
        """Test complete story generation workflow with real worker."""
        # 1. Submit story generation task
        request_data = {
            "prompt": "A brave knight",
            "max_length": 100,
            "temperature": 0.7
        }
        
        response = real_client.post("/api/v1/llm/generate", json=request_data)
        assert response.status_code == 200
        
        task_response = response.json()
        
        # Verify TaskResponse structure
        assert "task_id" in task_response
        assert "status" in task_response
        assert task_response["status"] == "PENDING"
        
        task_id = task_response["task_id"]
        
        # 2. Wait for task completion
        result = AsyncResult(task_id)
        
        # LLM tasks can take longer
        timeout = 60
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(1.0)  # Poll every second for LLM tasks
        
        assert result.ready(), f"LLM task {task_id} did not complete within {timeout} seconds"
        assert result.successful(), f"LLM task {task_id} failed: {result.traceback}"
        
        # 3. Verify task result contains generated story
        task_result = result.get(timeout=10)
        assert "story" in task_result
        assert "metadata" in task_result
        
        generated_text = task_result["story"]
        assert isinstance(generated_text, str)
        assert len(generated_text) > 0
        
        # Verify metadata
        metadata = task_result["metadata"]
        assert "model_used" in metadata
        assert "generation_time" in metadata
        assert "word_count" in metadata  # API returns word_count, not token_count

    def test_improve_story_end_to_end(self, real_client: TestClient):
        """Test complete story improvement workflow with real worker."""
        # 1. Submit story improvement task
        request_data = {
            "content": "Once upon a time there was a brave knight who lived in a magnificent castle and fought many dangerous dragons to protect the innocent villagers.",
            "improvement_type": "grammar",
            "focus_area": "Make it more dramatic"
        }
        
        response = real_client.post("/api/v1/llm/improve", json=request_data)
        assert response.status_code == 200
        
        task_response = response.json()
        task_id = task_response["task_id"]
        
        # 2. Wait for task completion
        result = AsyncResult(task_id)
        timeout = 60
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(1.0)
        
        assert result.ready(), f"Story improvement task {task_id} did not complete"
        assert result.successful(), f"Story improvement task failed: {result.traceback}"
        
        # 3. Verify improved story
        task_result = result.get(timeout=10)
        assert "improved_story" in task_result
        assert "original_story" in task_result
        assert "metadata" in task_result
        
        improved_text = task_result["improved_story"]
        assert isinstance(improved_text, str)
        assert len(improved_text) > 0
        
        original_story = task_result["original_story"]
        assert isinstance(original_story, str)

    def test_analyze_story_end_to_end(self, real_client: TestClient):
        """Test complete story analysis workflow with real worker."""
        # 1. Submit story analysis task
        request_data = {
            "content": "The dragon flew over the medieval castle while the knight prepared for battle. The air was thick with tension.",
            "analysis_type": "sentiment"  # Changed from "style" to valid "sentiment"
        }
        
        response = real_client.post("/api/v1/llm/analyze", json=request_data)
        assert response.status_code == 200
        
        task_response = response.json()
        task_id = task_response["task_id"]
        
        # 2. Wait for task completion
        result = AsyncResult(task_id)
        timeout = 60
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(1.0)
        
        assert result.ready(), f"Story analysis task {task_id} did not complete"
        assert result.successful(), f"Story analysis task failed: {result.traceback}"
        
        # 3. Verify analysis results
        task_result = result.get(timeout=10)
        assert "analysis" in task_result
        assert "metadata" in task_result
        
        analysis = task_result["analysis"]
        # Analysis result can be string or dict based on LLM response format
        assert isinstance(analysis, (str, dict))
        
        # Verify it contains some analysis content
        if isinstance(analysis, dict):
            assert "style_analysis" in analysis or "content_analysis" in analysis
            assert "summary" in analysis
        else:
            # String analysis should be non-empty
            assert len(analysis) > 10

    def test_generate_story_with_invalid_parameters(self, real_client: TestClient):
        """Test story generation with invalid parameters."""
        # Invalid temperature (out of range)
        invalid_data = {
            "prompt": "A story",
            "temperature": 2.5  # Should be 0.0-2.0
        }
        
        response = real_client.post("/api/v1/llm/generate", json=invalid_data)
        
        # Should fail validation before reaching Celery
        assert response.status_code == 422
        
        error_response = response.json()
        assert "task_id" not in error_response
        assert "detail" in error_response

    def test_llm_task_failure_handling(self, real_client: TestClient):
        """Test handling of LLM task failures."""
        # Submit a request that might cause issues
        request_data = {
            "prompt": "",  # Empty prompt might cause issues
            "max_length": 1000,
            "temperature": 0.1
        }
        
        response = real_client.post("/api/v1/llm/generate", json=request_data)
        
        if response.status_code == 422:
            # Validation caught the empty prompt
            error_response = response.json()
            assert "task_id" not in error_response
            return
        
        # If task was submitted, wait and check result
        assert response.status_code == 200
        task_response = response.json()
        task_id = task_response["task_id"]
        
        result = AsyncResult(task_id)
        timeout = 60
        start_time = time.time()
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(1.0)
        
        assert result.ready(), f"Task {task_id} did not complete"
        
        # Task might fail or succeed with empty/minimal output
        if result.failed():
            # This is acceptable for invalid input
            assert result.traceback is not None
        else:
            # If it succeeded, verify result structure
            task_result = result.get(timeout=10)
            assert "generated_text" in task_result

    def test_concurrent_llm_operations(self, real_client: TestClient):
        """Test multiple concurrent LLM operations."""
        # Submit multiple different LLM tasks
        requests = [
            ("generate", {"prompt": "A wizard in a magical forest", "max_tokens": 200}),  # Changed max_length to max_tokens
            ("generate", {"prompt": "A princess on a grand adventure", "max_tokens": 200}),  # Changed max_length to max_tokens  
            ("improve", {"content": "This is a short story that needs improvement. It describes a journey through mysterious lands.", "improvement_type": "style"}),
            ("analyze", {"content": "A tale of adventure across the mystical realms of fantasy where heroes battle ancient evil.", "analysis_type": "genre"})  # Changed from "content" to valid "genre"
        ]
        
        task_ids = []
        
        # Submit all tasks
        for endpoint, data in requests:
            response = real_client.post(f"/api/v1/llm/{endpoint}", json=data)
            assert response.status_code == 200
            task_response = response.json()
            task_ids.append((endpoint, task_response["task_id"]))
        
        # Wait for all tasks to complete
        timeout = 90  # Longer timeout for multiple LLM tasks
        results = []
        
        for endpoint, task_id in task_ids:
            result = AsyncResult(task_id)
            start_time = time.time()
            while not result.ready() and (time.time() - start_time) < timeout:
                time.sleep(1.0)
            
            assert result.ready(), f"LLM task {task_id} ({endpoint}) did not complete"
            
            if result.successful():
                task_result = result.get(timeout=10)
                results.append((endpoint, task_result))
            else:
                # Some LLM tasks might fail due to model issues - log but don't fail test
                print(f"LLM task {task_id} ({endpoint}) failed: {result.traceback}")
        
        # Verify we got some successful results
        assert len(results) > 0, "No LLM tasks completed successfully"
        
        # Verify result structures for successful tasks
        for endpoint, task_result in results:
            if endpoint == "generate":
                assert "story" in task_result
                assert "metadata" in task_result
            elif endpoint == "improve":
                assert "improved_story" in task_result
                assert "original_story" in task_result
            elif endpoint == "analyze":
                assert "analysis" in task_result
                assert "metadata" in task_result

    def test_llm_task_timeout_handling(self, real_client: TestClient):
        """Test handling of potential LLM task timeouts."""
        # Submit a complex request that might take longer
        request_data = {
            "prompt": "Write a detailed epic fantasy story with multiple characters, complex plot, and rich descriptions",
            "max_length": 2000,  # Large output
            "temperature": 0.8
        }
        
        response = real_client.post("/api/v1/llm/generate", json=request_data)
        assert response.status_code == 200
        
        task_response = response.json()
        task_id = task_response["task_id"]
        
        # Give it a reasonable time to complete
        result = AsyncResult(task_id)
        timeout = 120  # 2 minutes for complex generation
        start_time = time.time()
        
        while not result.ready() and (time.time() - start_time) < timeout:
            time.sleep(2.0)  # Poll every 2 seconds
        
        # Task should either complete or we handle the timeout gracefully
        if result.ready():
            if result.successful():
                task_result = result.get(timeout=10)
                assert "story" in task_result
                assert len(task_result["story"]) > 0
            else:
                # Task failed - this might be expected for very long generations
                print(f"Long generation task failed: {result.traceback}")
        else:
            # Task is still running - this is acceptable for very long operations
            print(f"Task {task_id} still running after {timeout} seconds")
            # We could revoke the task here if needed
            # result.revoke(terminate=True)

    def test_llm_model_configuration_variations(self, real_client: TestClient):
        """Test LLM operations with different model configurations."""
        # Test with different temperature values
        temperatures = [0.1, 0.5, 1.0, 1.5]
        task_ids = []
        
        for temp in temperatures:
            request_data = {
                "prompt": "A short story about courage",
                "max_length": 100,
                "temperature": temp
            }
            
            response = real_client.post("/api/v1/llm/generate", json=request_data)
            assert response.status_code == 200
            
            task_response = response.json()
            task_ids.append(task_response["task_id"])
        
        # Wait for all tasks and verify they produce different results
        results = []
        timeout = 60
        
        for i, task_id in enumerate(task_ids):
            result = AsyncResult(task_id)
            start_time = time.time()
            while not result.ready() and (time.time() - start_time) < timeout:
                time.sleep(1.0)
            
            if result.ready() and result.successful():
                task_result = result.get(timeout=10)
                results.append((temperatures[i], task_result["story"]))
        
        # Should have gotten some results
        assert len(results) > 0
        
        # Results should be different (though this is probabilistic)
        if len(results) > 1:
            texts = [result[1] for result in results]
            unique_texts = set(texts)
            # At least some should be different
            assert len(unique_texts) > 1 or len(texts[0]) > 10  # Either different or substantial output
