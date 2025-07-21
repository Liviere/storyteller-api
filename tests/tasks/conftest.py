"""
Test configuration for Celery tasks and task service.
"""

import pytest
from unittest.mock import Mock, patch
from celery import Celery
from celery.result import AsyncResult

from app.services.task_service import TaskService
from app.celery_app.celery import celery_app


@pytest.fixture
def mock_celery_app():
    """Mock Celery app for testing."""
    mock_app = Mock(spec=Celery)
    mock_app.send_task = Mock()
    mock_app.control = Mock()
    mock_app.control.inspect = Mock()
    return mock_app


@pytest.fixture
def mock_async_result():
    """Mock AsyncResult for testing."""
    mock_result = Mock(spec=AsyncResult)
    mock_result.status = "SUCCESS"
    mock_result.result = {"test": "result"}
    mock_result.info = None
    mock_result.traceback = None
    mock_result.ready.return_value = True
    mock_result.successful.return_value = True
    mock_result.failed.return_value = False
    mock_result.get.return_value = {"test": "result"}
    return mock_result


@pytest.fixture
def task_service(mock_celery_app):
    """TaskService instance with mocked Celery app."""
    service = TaskService()
    service.celery_app = mock_celery_app
    return service


@pytest.fixture
def mock_task_id():
    """Sample task ID for testing."""
    return "test-task-id-12345"


# Celery testing configuration
@pytest.fixture(scope="session")
def celery_config():
    """Celery configuration for testing."""
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        'task_always_eager': True,
        'task_eager_propagates': True,
    }


@pytest.fixture(scope="session") 
def celery_app_test(celery_config):
    """Test Celery app instance."""
    from app.celery_app.celery import create_celery_app
    
    app = create_celery_app()
    app.config_from_object(celery_config)
    
    # Override with test config
    app.conf.update(celery_config)
    
    return app


@pytest.fixture
def celery_worker_test(celery_app_test):
    """Test Celery worker."""
    with celery_app_test.Worker(
        broker=celery_app_test.conf.broker_url,
        perform_ping_check=False
    ) as worker:
        yield worker
