"""
Integration tests for Celery tasks with real worker.

These tests use pytest-celery to set up real Celery workers and test
actual task execution. They require Redis to be running.
"""

import pytest
import asyncio
from unittest.mock import patch, Mock

from app.celery_app.tasks.llm import (
    generate_story_task,
    analyze_story_task, 
    summarize_story_task,
    improve_story_task
)
from app.celery_app.tasks.stories import (
    create_story_task,
    update_story_task,
    delete_story_task,
    patch_story_task
)


@pytest.mark.integration
@pytest.mark.celery_integration
class TestLLMTasksIntegration:
    """Integration tests for LLM Celery tasks."""
    
    @pytest.fixture
    def celery_config(self):
        """Celery configuration for integration tests."""
        return {
            'broker_url': 'redis://localhost:6379/0',
            'result_backend': 'redis://localhost:6379/0',
            'task_always_eager': True,  # Execute tasks synchronously for testing
            'task_eager_propagates': True,  # Propagate exceptions
        }
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service for integration tests."""
        mock_service = Mock()
        
        # Mock async methods
        async def mock_generate_story(**kwargs):
            return {
                "story": "Integration test generated story",
                "metadata": {"model": "test-model", "tokens": 100}
            }
        
        async def mock_analyze_story(**kwargs):
            return {
                "analysis": "Positive sentiment detected",
                "metadata": {"model": "test-model", "confidence": 0.95}
            }
        
        async def mock_summarize_story(**kwargs):
            return {
                "summary": "Brief summary of the story",
                "metadata": {"model": "test-model", "compression_ratio": 0.3}
            }
        
        async def mock_improve_story(**kwargs):
            return {
                "improved_content": "Improved version of the story",
                "metadata": {"model": "test-model", "changes_made": 5}
            }
        
        mock_service.generate_story = mock_generate_story
        mock_service.analyze_story = mock_analyze_story
        mock_service.summarize_story = mock_summarize_story
        mock_service.improve_story = mock_improve_story
        
        return mock_service
    
    def test_generate_story_task_execution(self, celery_worker, mock_llm_service):
        """Test generate_story_task executes successfully."""
        with patch('app.celery_app.tasks.llm.get_llm_service', return_value=mock_llm_service):
            result = generate_story_task.delay(
                prompt="Test story prompt",
                genre="fantasy",
                length="short"
            )
            
            assert result.ready()
            assert result.successful()
            
            task_result = result.get()
            assert task_result["success"] is True
            assert "story" in task_result
            assert task_result["story"] == "Integration test generated story"
    
    def test_analyze_story_task_execution(self, celery_worker, mock_llm_service):
        """Test analyze_story_task executes successfully."""
        with patch('app.celery_app.tasks.llm.get_llm_service', return_value=mock_llm_service):
            result = analyze_story_task.delay(
                content="Story content to analyze",
                analysis_type="sentiment"
            )
            
            assert result.ready()
            assert result.successful()
            
            task_result = result.get()
            assert task_result["success"] is True
            assert "analysis" in task_result
            assert "Positive sentiment" in task_result["analysis"]
    
    def test_summarize_story_task_execution(self, celery_worker, mock_llm_service):
        """Test summarize_story_task executes successfully."""
        with patch('app.celery_app.tasks.llm.get_llm_service', return_value=mock_llm_service):
            result = summarize_story_task.delay(
                content="Long story content to summarize",
                summary_length="brief"
            )
            
            assert result.ready() 
            assert result.successful()
            
            task_result = result.get()
            assert task_result["success"] is True
            assert "summary" in task_result
            assert task_result["summary"] == "Brief summary of the story"
    
    def test_improve_story_task_execution(self, celery_worker, mock_llm_service):
        """Test improve_story_task executes successfully."""
        with patch('app.celery_app.tasks.llm.get_llm_service', return_value=mock_llm_service):
            result = improve_story_task.delay(
                content="Story content to improve",
                improvement_type="grammar"
            )
            
            assert result.ready()
            assert result.successful()
            
            task_result = result.get()
            assert task_result["success"] is True
            assert "improved_content" in task_result
            assert task_result["improved_content"] == "Improved version of the story"
    
    def test_task_retry_on_failure(self, celery_worker):
        """Test that tasks retry on failure."""
        with patch('app.celery_app.tasks.llm.get_llm_service') as mock_get_service:
            mock_service = Mock()
            
            # Mock the async method to raise an exception
            async def failing_generate(**kwargs):
                raise Exception("Service temporarily unavailable")
            
            mock_service.generate_story = failing_generate
            mock_get_service.return_value = mock_service
            
            # The task should retry (configured in task definition)
            result = generate_story_task.delay(
                prompt="Test prompt",
                genre="fantasy"
            )
            
            # Task will eventually fail after retries
            assert result.ready()
            assert result.failed()
    
    def test_task_parameter_validation(self, celery_worker, mock_llm_service):
        """Test task parameter validation."""
        with patch('app.celery_app.tasks.llm.get_llm_service', return_value=mock_llm_service):
            # Test with invalid analysis type
            result = analyze_story_task.delay(
                content="Story content",
                analysis_type="invalid_type"
            )
            
            assert result.ready()
            assert result.failed()


@pytest.mark.integration  
@pytest.mark.celery_integration
class TestStoryTasksIntegration:
    """Integration tests for Story Celery tasks."""
    
    @pytest.fixture
    def celery_config(self):
        """Celery configuration for integration tests."""
        return {
            'broker_url': 'redis://localhost:6379/0',
            'result_backend': 'redis://localhost:6379/0', 
            'task_always_eager': True,
            'task_eager_propagates': True,
        }
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for story tasks."""
        from unittest.mock import Mock
        from app.models.story import Story
        
        mock_session = Mock()
        
        # Mock story instance
        mock_story = Mock(spec=Story)
        mock_story.id = 1
        mock_story.title = "Test Story"
        mock_story.content = "Test content"
        mock_story.author = "Test Author"
        mock_story.genre = "Fiction"
        mock_story.is_published = False
        
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_story
        mock_session.delete = Mock()
        
        return mock_session, mock_story
    
    @pytest.mark.skip(reason="Requires database setup - implement after DB test fixtures")
    def test_create_story_task_execution(self, celery_worker, mock_db_session):
        """Test create_story_task executes successfully."""
        mock_session, mock_story = mock_db_session
        
        with patch('app.celery_app.tasks.stories.get_db_session', return_value=mock_session):
            story_data = {
                "title": "Test Story",
                "content": "Test content",
                "author": "Test Author",
                "genre": "Fiction"
            }
            
            result = create_story_task.delay(story_data)
            
            assert result.ready()
            assert result.successful()
            
            task_result = result.get()
            assert task_result["success"] is True
            assert "story_id" in task_result
    
    @pytest.mark.skip(reason="Requires database setup")  
    def test_update_story_task_execution(self, celery_worker, mock_db_session):
        """Test update_story_task executes successfully."""
        mock_session, mock_story = mock_db_session
        
        with patch('app.celery_app.tasks.stories.get_db_session', return_value=mock_session):
            story_data = {"title": "Updated Title"}
            
            result = update_story_task.delay(1, story_data)
            
            assert result.ready()
            assert result.successful()
            
            task_result = result.get()
            assert task_result["success"] is True
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_delete_story_task_execution(self, celery_worker, mock_db_session):
        """Test delete_story_task executes successfully."""
        mock_session, mock_story = mock_db_session
        
        with patch('app.celery_app.tasks.stories.get_db_session', return_value=mock_session):
            result = delete_story_task.delay(1)
            
            assert result.ready()
            assert result.successful()
            
            task_result = result.get()
            assert task_result["success"] is True


@pytest.mark.integration
@pytest.mark.celery_worker  
class TestTaskServiceIntegration:
    """Integration tests for TaskService with real Celery."""
    
    @pytest.fixture
    def real_task_service(self):
        """Real TaskService instance for integration testing."""
        from app.services.task_service import TaskService
        return TaskService()
    
    def test_task_submission_and_status_check(self, real_task_service, mock_llm_service):
        """Test submitting task and checking its status."""
        with patch('app.celery_app.tasks.llm.get_llm_service', return_value=mock_llm_service):
            # Submit task
            task_id = real_task_service.generate_story_async(
                prompt="Integration test story",
                genre="fantasy"
            )
            
            assert task_id is not None
            assert isinstance(task_id, str)
            
            # Check status
            status = real_task_service.get_task_status(task_id)
            assert status["task_id"] == task_id
            assert status["status"] in ["PENDING", "SUCCESS", "FAILURE"]
    
    def test_task_result_retrieval(self, real_task_service, mock_llm_service):
        """Test retrieving task results."""
        with patch('app.celery_app.tasks.llm.get_llm_service', return_value=mock_llm_service):
            # Submit and wait for task
            task_id = real_task_service.generate_story_async(
                prompt="Test prompt",
                genre="fantasy"
            )
            
            # Get result (with eager execution, this should complete immediately)
            result = real_task_service.get_task_result(task_id, timeout=10)
            
            assert result is not None
            assert "success" in result
            assert result["success"] is True


@pytest.mark.integration
@pytest.mark.slow
class TestCeleryWorkerHealth:
    """Integration tests for Celery worker health and connectivity."""
    
    def test_worker_ping(self, celery_worker):
        """Test that worker responds to ping."""
        from app.celery_app.celery import celery_app
        
        # Test ping
        inspect = celery_app.control.inspect()
        ping_result = inspect.ping()
        
        assert ping_result is not None
        # With eager execution, inspect may return None or worker info
    
    def test_registered_tasks(self, celery_worker):
        """Test that all expected tasks are registered."""
        from app.celery_app.celery import celery_app
        
        expected_tasks = [
            'llm.generate_story',
            'llm.analyze_story', 
            'llm.summarize_story',
            'llm.improve_story',
            'stories.create_story',
            'stories.update_story',
            'stories.delete_story',
            'stories.patch_story'
        ]
        
        registered_tasks = list(celery_app.tasks.keys())
        
        for expected_task in expected_tasks:
            assert any(expected_task in task for task in registered_tasks), f"Task {expected_task} not registered"


# Pytest markers for conditional test execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        "not config.getoption('--integration')",
        reason="Integration tests require --integration flag"
    )
]
