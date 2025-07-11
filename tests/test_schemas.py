"""
Tests for Pydantic schemas.
"""
from datetime import datetime

import pytest
from pydantic import ValidationError

from schemas.story import StoryBase, StoryCreate, StoryResponse, StoryUpdate


class TestStorySchemas:
    """Test cases for Story schemas."""

    def test_story_base_valid_data(self):
        """Test StoryBase with valid data."""
        data = {
            "title": "Test Story",
            "content": "This is test content.",
            "author": "Test Author",
            "genre": "Fiction",
            "is_published": False
        }
        
        story = StoryBase(**data)
        
        assert story.title == "Test Story"
        assert story.content == "This is test content."
        assert story.author == "Test Author"
        assert story.genre == "Fiction"
        assert story.is_published is False

    def test_story_base_optional_fields(self):
        """Test StoryBase with optional fields."""
        data = {
            "title": "Test Story",
            "content": "This is test content.",
            "author": "Test Author"
            # genre is optional, is_published has default
        }
        
        story = StoryBase(**data)
        
        assert story.title == "Test Story"
        assert story.content == "This is test content."
        assert story.author == "Test Author"
        assert story.genre is None
        assert story.is_published is False  # Default value

    def test_story_base_field_validation(self):
        """Test field validation in StoryBase."""
        # Test empty title
        with pytest.raises(ValidationError):
            StoryBase(
                title="",
                content="Test content",
                author="Test Author"
            )
        
        # Test empty content
        with pytest.raises(ValidationError):
            StoryBase(
                title="Test Title",
                content="",
                author="Test Author"
            )
        
        # Test empty author
        with pytest.raises(ValidationError):
            StoryBase(
                title="Test Title",
                content="Test content",
                author=""
            )

    def test_story_base_field_length_limits(self):
        """Test field length limits in StoryBase."""
        # Test title too long (max 200 characters)
        with pytest.raises(ValidationError):
            StoryBase(
                title="a" * 201,
                content="Test content",
                author="Test Author"
            )
        
        # Test author too long (max 100 characters)
        with pytest.raises(ValidationError):
            StoryBase(
                title="Test Title",
                content="Test content",
                author="a" * 101
            )
        
        # Test genre too long (max 50 characters)
        with pytest.raises(ValidationError):
            StoryBase(
                title="Test Title",
                content="Test content",
                author="Test Author",
                genre="a" * 51
            )

    def test_story_create_schema(self):
        """Test StoryCreate schema."""
        data = {
            "title": "Test Story",
            "content": "Test content",
            "author": "Test Author",
            "genre": "Fiction"
        }
        
        story = StoryCreate(**data)
        
        assert story.title == "Test Story"
        assert story.content == "Test content"
        assert story.author == "Test Author"
        assert story.genre == "Fiction"

    def test_story_update_schema(self):
        """Test StoryUpdate schema with partial data."""
        # Test updating only title
        update_data = {"title": "Updated Title"}
        story_update = StoryUpdate(**update_data)
        
        assert story_update.title == "Updated Title"
        assert story_update.content is None
        assert story_update.author is None
        assert story_update.genre is None
        assert story_update.is_published is None

    def test_story_update_all_fields(self):
        """Test StoryUpdate schema with all fields."""
        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "author": "Updated Author",
            "genre": "Updated Genre",
            "is_published": True
        }
        
        story_update = StoryUpdate(**update_data)
        
        assert story_update.title == "Updated Title"
        assert story_update.content == "Updated content"
        assert story_update.author == "Updated Author"
        assert story_update.genre == "Updated Genre"
        assert story_update.is_published is True

    def test_story_update_validation(self):
        """Test validation in StoryUpdate schema."""
        # Test empty title (should fail)
        with pytest.raises(ValidationError):
            StoryUpdate(title="")
        
        # Test empty content (should fail)
        with pytest.raises(ValidationError):
            StoryUpdate(content="")
        
        # Test empty author (should fail)
        with pytest.raises(ValidationError):
            StoryUpdate(author="")

    def test_story_response_schema(self):
        """Test StoryResponse schema."""
        data = {
            "id": 1,
            "title": "Test Story",
            "content": "Test content",
            "author": "Test Author",
            "genre": "Fiction",
            "is_published": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        story_response = StoryResponse(**data)
        
        assert story_response.id == 1
        assert story_response.title == "Test Story"
        assert story_response.content == "Test content"
        assert story_response.author == "Test Author"
        assert story_response.genre == "Fiction"
        assert story_response.is_published is True
        assert isinstance(story_response.created_at, datetime)
        assert isinstance(story_response.updated_at, datetime)

    def test_story_response_without_updated_at(self):
        """Test StoryResponse schema without updated_at."""
        data = {
            "id": 1,
            "title": "Test Story",
            "content": "Test content",
            "author": "Test Author",
            "genre": "Fiction",
            "is_published": False,
            "created_at": datetime.now()
        }
        
        story_response = StoryResponse(**data)
        
        assert story_response.id == 1
        assert story_response.updated_at is None
