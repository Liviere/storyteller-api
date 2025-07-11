"""
Tests for Story model.
"""
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.story import Story


class TestStoryModel:
    """Test cases for Story model."""

    def test_create_story(self, db_session):
        """Test creating a new story."""
        story = Story(
            title="Test Story",
            content="This is test content.",
            author="Test Author",
            genre="Fiction"
        )
        
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        
        assert story.id is not None
        assert story.title == "Test Story"
        assert story.content == "This is test content."
        assert story.author == "Test Author"
        assert story.genre == "Fiction"
        assert story.is_published is False  # Default value
        assert isinstance(story.created_at, datetime)

    def test_story_repr(self, db_session):
        """Test story string representation."""
        story = Story(
            title="Test Story",
            content="Test content",
            author="Test Author"
        )
        
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        
        expected_repr = f"<Story(id={story.id}, title='Test Story', author='Test Author')>"
        assert str(story) == expected_repr

    def test_story_required_fields(self, db_session):
        """Test that required fields are enforced."""
        # Test missing title
        story = Story(
            content="Test content",
            author="Test Author"
        )
        db_session.add(story)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing content
        story = Story(
            title="Test Title",
            author="Test Author"
        )
        db_session.add(story)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing author
        story = Story(
            title="Test Title",
            content="Test content"
        )
        db_session.add(story)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_story_optional_fields(self, db_session):
        """Test that optional fields work correctly."""
        story = Story(
            title="Test Story",
            content="Test content",
            author="Test Author"
            # genre is optional
        )
        
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        
        assert story.genre is None
        assert story.is_published is False  # Default value

    def test_story_published_flag(self, db_session):
        """Test the published flag functionality."""
        story = Story(
            title="Test Story",
            content="Test content",
            author="Test Author",
            is_published=True
        )
        
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        
        assert story.is_published is True

    def test_story_timestamps(self, db_session):
        """Test that timestamps are set correctly."""
        import time
        
        story = Story(
            title="Test Story",
            content="Test content",
            author="Test Author"
        )
        
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        
        assert story.created_at is not None
        assert isinstance(story.created_at, datetime)
        
        # Update the story after a small delay
        original_created_at = story.created_at
        time.sleep(0.01)  # Small delay to ensure different timestamps
        story.title = "Updated Title"
        db_session.commit()
        db_session.refresh(story)
        
        # created_at should remain the same
        assert story.created_at == original_created_at
        # updated_at should be set
        assert story.updated_at is not None
        assert isinstance(story.updated_at, datetime)
        # Note: In SQLite with default precision, timestamps might be the same
        # This is acceptable behavior
