"""
Test configuration and fixtures for Story Teller API tests.

This module provides common fixtures and configuration for all tests,
including database setup, test client, and Celery testing utilities.
"""

import os
import tempfile
from typing import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import get_db
from app.models.story import Base
from app.services.task_service import get_task_service
from main import app


def get_test_database_url():
    """Get test database URL based on environment."""
    # Check if we should use MySQL for testing (e.g., in CI/CD)
    test_mysql_url = os.getenv("TEST_DATABASE_URL")
    if test_mysql_url and "mysql" in test_mysql_url:
        return test_mysql_url

    # Default to SQLite for local testing
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    return f"sqlite:///{temp_file.name}"


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    test_database_url = get_test_database_url()

    if "mysql" in test_database_url:
        # MySQL configuration for testing
        engine = create_engine(
            test_database_url,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        cleanup_file = None
    else:
        # SQLite configuration for testing
        engine = create_engine(
            test_database_url, connect_args={"check_same_thread": False}
        )
        cleanup_file = test_database_url.replace("sqlite:///", "")

    # Create tables
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestingSessionLocal, engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    if cleanup_file and os.path.exists(cleanup_file):
        os.unlink(cleanup_file)


@pytest.fixture
def db_session(temp_db):
    """Create a database session for testing."""
    TestingSessionLocal, engine = temp_db
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(temp_db) -> Generator[TestClient, None, None]:
    """Create a test client with a temporary database."""
    TestingSessionLocal, engine = temp_db

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_story_data():
    """Sample story data for testing."""
    return {
        "title": "Test Story",
        "content": "This is a test story content.",
        "author": "Test Author",
        "genre": "Fiction",
        "is_published": False,
    }


@pytest.fixture
def sample_stories_data():
    """Multiple sample stories for testing."""
    return [
        {
            "title": "Fantasy Adventure",
            "content": "A tale of magic and dragons.",
            "author": "Fantasy Author",
            "genre": "Fantasy",
            "is_published": True,
        },
        {
            "title": "Sci-Fi Journey",
            "content": "A story about space exploration.",
            "author": "Sci-Fi Author",
            "genre": "Science Fiction",
            "is_published": False,
        },
        {
            "title": "Mystery Novel",
            "content": "A thrilling mystery story.",
            "author": "Mystery Author",
            "genre": "Mystery",
            "is_published": True,
        },
    ]


# Celery testing fixtures
@pytest.fixture
def mock_task_service():
    """Mock TaskService for testing async endpoints."""
    mock_service = Mock()
    mock_service.generate_story_async.return_value = "mock-task-id-123"
    mock_service.analyze_story_async.return_value = "mock-task-id-456" 
    mock_service.summarize_story_async.return_value = "mock-task-id-789"
    mock_service.improve_story_async.return_value = "mock-task-id-abc"
    mock_service.create_story_async.return_value = "mock-story-task-123"
    mock_service.update_story_async.return_value = "mock-story-task-456"
    mock_service.delete_story_async.return_value = "mock-story-task-789"
    mock_service.patch_story_async.return_value = "mock-story-task-abc"
    
    # Mock status and result methods
    mock_service.get_task_status.return_value = {
        "task_id": "mock-task-id",
        "status": "SUCCESS", 
        "result": {"success": True, "data": "mock result"},
        "successful": True,
        "failed": False
    }
    mock_service.get_task_result.return_value = {"success": True, "data": "mock result"}
    mock_service.cancel_task.return_value = True
    
    return mock_service


@pytest.fixture
def override_task_service(mock_task_service):
    """Override TaskService dependency with mock."""
    app.dependency_overrides[get_task_service] = lambda: mock_task_service
    yield mock_task_service
    if get_task_service in app.dependency_overrides:
        del app.dependency_overrides[get_task_service]


# Command line options for pytest
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--integration",
        action="store_true", 
        default=False,
        help="Run integration tests"
    )
    parser.addoption(
        "--celery",
        action="store_true",
        default=False, 
        help="Run tests requiring Celery worker"
    )


def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "celery_integration: mark test as requiring Celery worker"
    )
