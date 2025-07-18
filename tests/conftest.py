"""
Test configuration and fixtures for Story Teller API tests.
"""

import os
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import get_db
from app.models.story import Base
from main import app

# Import LLM-specific fixtures
pytest_plugins = ["tests.llm.conftest_llm"]

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
