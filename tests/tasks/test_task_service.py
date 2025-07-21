"""
Unit tests for TaskService.

These tests use mocking to test TaskService functionality without 
requiring a real Celery worker or broker.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from celery.result import AsyncResult

from app.services.task_service import TaskService, get_task_service


class TestTaskServiceInitialization:
    """Test TaskService initialization and singleton behavior."""
    
    def test_task_service_initialization(self):
        """Test TaskService can be initialized."""
        service = TaskService()
        assert service is not None
        assert hasattr(service, 'celery_app')
    
    def test_get_task_service_singleton(self):
        """Test get_task_service returns same instance."""
        service1 = get_task_service()
        service2 = get_task_service()
        assert service1 is service2


class TestTaskServiceTaskStatus:
    """Test task status retrieval methods."""
    
    def test_get_task_status_success(self, task_service, mock_task_id, mock_async_result):
        """Test getting status of successful task."""
        with patch('app.services.task_service.AsyncResult', return_value=mock_async_result):
            status = task_service.get_task_status(mock_task_id)
            
            assert status['task_id'] == mock_task_id
            assert status['status'] == 'SUCCESS'
            assert status['result'] == {'test': 'result'}
            assert status['successful'] is True
            assert status['failed'] is False
    
    def test_get_task_status_pending(self, task_service, mock_task_id):
        """Test getting status of pending task."""
        mock_result = Mock(spec=AsyncResult)
        mock_result.status = 'PENDING'
        mock_result.result = None
        mock_result.ready.return_value = False
        mock_result.successful.return_value = None
        mock_result.failed.return_value = None
        
        with patch('app.services.task_service.AsyncResult', return_value=mock_result):
            status = task_service.get_task_status(mock_task_id)
            
            assert status['status'] == 'PENDING'
            assert status['result'] is None
            assert status['successful'] is None
            assert status['failed'] is None
    
    def test_get_task_result_success(self, task_service, mock_task_id, mock_async_result):
        """Test getting result of completed task."""
        with patch('app.services.task_service.AsyncResult', return_value=mock_async_result):
            result = task_service.get_task_result(mock_task_id)
            assert result == {'test': 'result'}
    
    def test_get_task_result_with_timeout(self, task_service, mock_task_id, mock_async_result):
        """Test getting result with timeout."""
        with patch('app.services.task_service.AsyncResult', return_value=mock_async_result):
            result = task_service.get_task_result(mock_task_id, timeout=10)
            mock_async_result.get.assert_called_with(timeout=10)
    
    def test_cancel_task(self, task_service, mock_task_id):
        """Test task cancellation."""
        mock_result = Mock(spec=AsyncResult)
        mock_result.revoke = Mock()
        
        with patch('app.services.task_service.AsyncResult', return_value=mock_result):
            success = task_service.cancel_task(mock_task_id)
            
            assert success is True
            mock_result.revoke.assert_called_once_with(terminate=True)


class TestTaskServiceWorkerInfo:
    """Test worker information methods."""
    
    def test_get_active_tasks(self, task_service):
        """Test getting active tasks information."""
        mock_inspect = Mock()
        mock_inspect.active.return_value = {'worker1': []}
        mock_inspect.scheduled.return_value = {'worker1': []}
        mock_inspect.reserved.return_value = {'worker1': []}
        
        task_service.celery_app.control.inspect.return_value = mock_inspect
        
        result = task_service.get_active_tasks()
        
        assert 'active' in result
        assert 'scheduled' in result
        assert 'reserved' in result
    
    def test_get_worker_stats(self, task_service):
        """Test getting worker statistics."""
        mock_inspect = Mock()
        mock_inspect.stats.return_value = {'worker1': {}}
        mock_inspect.ping.return_value = {'worker1': 'pong'}
        mock_inspect.registered.return_value = {'worker1': []}
        
        task_service.celery_app.control.inspect.return_value = mock_inspect
        
        result = task_service.get_worker_stats()
        
        assert 'stats' in result
        assert 'ping' in result
        assert 'registered' in result


class TestTaskServiceStoryTasks:
    """Test story-related task submission methods."""
    
    def test_create_story_async(self, task_service):
        """Test submitting story creation task."""
        story_data = {'title': 'Test Story', 'content': 'Test content'}
        mock_task = Mock()
        mock_task.id = 'task-123'
        
        task_service.celery_app.send_task.return_value = mock_task
        
        task_id = task_service.create_story_async(story_data)
        
        assert task_id == 'task-123'
        task_service.celery_app.send_task.assert_called_once_with(
            'stories.create_story',
            args=[story_data]
        )
    
    def test_update_story_async(self, task_service):
        """Test submitting story update task."""
        story_id = 1
        story_data = {'title': 'Updated Story'}
        mock_task = Mock()
        mock_task.id = 'task-456'
        
        task_service.celery_app.send_task.return_value = mock_task
        
        task_id = task_service.update_story_async(story_id, story_data)
        
        assert task_id == 'task-456'
        task_service.celery_app.send_task.assert_called_once_with(
            'stories.update_story',
            args=[story_id, story_data, False]
        )
    
    def test_delete_story_async(self, task_service):
        """Test submitting story deletion task."""
        story_id = 1
        mock_task = Mock()
        mock_task.id = 'task-789'
        
        task_service.celery_app.send_task.return_value = mock_task
        
        task_id = task_service.delete_story_async(story_id)
        
        assert task_id == 'task-789'
        task_service.celery_app.send_task.assert_called_once_with(
            'stories.delete_story',
            args=[story_id, False]
        )
    
    def test_patch_story_async(self, task_service):
        """Test submitting story patch task."""
        story_id = 1
        patch_data = {'is_published': True}
        mock_task = Mock()
        mock_task.id = 'task-abc'
        
        task_service.celery_app.send_task.return_value = mock_task
        
        task_id = task_service.patch_story_async(story_id, patch_data)
        
        assert task_id == 'task-abc'
        task_service.celery_app.send_task.assert_called_once_with(
            'stories.patch_story',
            args=[story_id, patch_data]
        )


class TestTaskServiceLLMTasks:
    """Test LLM-related task submission methods."""
    
    def test_generate_story_async(self, task_service):
        """Test submitting story generation task."""
        kwargs = {
            'prompt': 'Test prompt',
            'genre': 'fantasy',
            'length': 'short'
        }
        mock_task = Mock()
        mock_task.id = 'llm-task-123'
        
        task_service.celery_app.send_task.return_value = mock_task
        
        task_id = task_service.generate_story_async(**kwargs)
        
        assert task_id == 'llm-task-123'
        task_service.celery_app.send_task.assert_called_once_with(
            'llm.generate_story',
            kwargs=kwargs
        )
    
    def test_analyze_story_async(self, task_service):
        """Test submitting story analysis task."""
        kwargs = {
            'content': 'Story content to analyze',
            'analysis_type': 'sentiment'
        }
        mock_task = Mock()
        mock_task.id = 'llm-task-456'
        
        task_service.celery_app.send_task.return_value = mock_task
        
        task_id = task_service.analyze_story_async(**kwargs)
        
        assert task_id == 'llm-task-456'
        task_service.celery_app.send_task.assert_called_once_with(
            'llm.analyze_story',
            kwargs=kwargs
        )
    
    def test_summarize_story_async(self, task_service):
        """Test submitting story summarization task."""
        kwargs = {
            'content': 'Long story content',
            'summary_length': 'brief'
        }
        mock_task = Mock()
        mock_task.id = 'llm-task-789'
        
        task_service.celery_app.send_task.return_value = mock_task
        
        task_id = task_service.summarize_story_async(**kwargs)
        
        assert task_id == 'llm-task-789'
        task_service.celery_app.send_task.assert_called_once_with(
            'llm.summarize_story',
            kwargs=kwargs
        )
    
    def test_improve_story_async(self, task_service):
        """Test submitting story improvement task."""
        kwargs = {
            'content': 'Story to improve',
            'improvement_type': 'grammar'
        }
        mock_task = Mock()
        mock_task.id = 'llm-task-abc'
        
        task_service.celery_app.send_task.return_value = mock_task
        
        task_id = task_service.improve_story_async(**kwargs)
        
        assert task_id == 'llm-task-abc'
        task_service.celery_app.send_task.assert_called_once_with(
            'llm.improve_story',
            kwargs=kwargs
        )
