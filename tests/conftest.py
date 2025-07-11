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

from database.connection import get_db
from main import app
from models.story import Base


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    
    test_database_url = f"sqlite:///{temp_file.name}"
    engine = create_engine(test_database_url, connect_args={"check_same_thread": False})
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal, engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    os.unlink(temp_file.name)


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
        "is_published": False
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
            "is_published": True
        },
        {
            "title": "Sci-Fi Journey",
            "content": "A story about space exploration.",
            "author": "Sci-Fi Author",
            "genre": "Science Fiction",
            "is_published": False
        },
        {
            "title": "Mystery Novel",
            "content": "A thrilling mystery story.",
            "author": "Mystery Author",
            "genre": "Mystery",
            "is_published": True
        }
    ]
