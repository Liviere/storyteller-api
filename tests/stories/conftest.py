"""
Stories-specific test fixtures and configuration.
"""

import pytest


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


@pytest.fixture
def db_with_stories(db_session, sample_stories_data):
    """Database session pre-populated with sample stories."""
    from app.models.story import Story

    stories = []
    for story_data in sample_stories_data:
        story = Story(**story_data)
        db_session.add(story)
        stories.append(story)

    db_session.commit()

    # Refresh to get IDs
    for story in stories:
        db_session.refresh(story)

    yield db_session, stories

    # Cleanup is handled by the parent db_session fixture
