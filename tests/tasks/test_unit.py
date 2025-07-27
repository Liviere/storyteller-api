"""
Unit tests for TaskService.
"""

import pytest
from unittest.mock import Mock, patch
from celery.result import AsyncResult

from app.services.task_service import TaskService, get_task_service

@pytest.mark.unit
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

@pytest.mark.unit
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

@pytest.mark.unit
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
