"""
Celery tasks for story operations
"""

from typing import Dict, Any
from app.celery_app.celery import celery_app
from app.database.connection import get_db
from app.models.story import Story
from app.schemas.story import StoryCreate, StoryUpdate
from sqlalchemy.orm import Session


@celery_app.task(bind=True, name="stories.create_story")
def create_story_task(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new story asynchronously
    
    Args:
        story_data: Dictionary containing story creation data
        
    Returns:
        Dictionary with created story data
    """
    try:
        db: Session = next(get_db())
        try:
            # Convert dict to Pydantic model
            story_create = StoryCreate(**story_data)
            
            # Create database entry
            db_story = Story(
                title=story_create.title,
                content=story_create.content,
                author=story_create.author,
                genre=story_create.genre,
                is_published=story_create.is_published or False
            )
            
            db.add(db_story)
            db.commit()
            db.refresh(db_story)
            
            return {
                "id": db_story.id,
                "title": db_story.title,
                "content": db_story.content,
                "author": db_story.author,
                "genre": db_story.genre,
                "is_published": db_story.is_published,
                "created_at": db_story.created_at.isoformat() if db_story.created_at else None,
                "updated_at": db_story.updated_at.isoformat() if db_story.updated_at else None
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        self.retry(countdown=60, max_retries=3, exc=exc)


@celery_app.task(bind=True, name="stories.update_story")
def update_story_task(self, story_id: int, story_data: Dict[str, Any], no_retry: bool = False) -> Dict[str, Any]:
    """
    Update an existing story asynchronously
    
    Args:
        story_id: ID of the story to update
        story_data: Dictionary containing update data
        no_retry: If True, disables retry behavior
        
    Returns:
        Dictionary with updated story data
    """
    try:
        db: Session = next(get_db())
        try:
            # Get existing story
            story = db.query(Story).filter(Story.id == story_id).first()
            if not story:
                raise ValueError(f"Story with id {story_id} not found")
            
            # Convert dict to Pydantic model
            story_update = StoryUpdate(**story_data)
            
            # Update fields that were provided
            update_data = story_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(story, field, value)
            
            db.commit()
            db.refresh(story)
            
            return {
                "id": story.id,
                "title": story.title,
                "content": story.content,
                "author": story.author,
                "genre": story.genre,
                "is_published": story.is_published,
                "created_at": story.created_at.isoformat() if story.created_at else None,
                "updated_at": story.updated_at.isoformat() if story.updated_at else None
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        if not no_retry:
            self.retry(countdown=60, max_retries=3, exc=exc)
        else:
            raise exc


@celery_app.task(bind=True, name="stories.delete_story")
def delete_story_task(self, story_id: int, no_retry: bool = False) -> Dict[str, Any]:
    """
    Delete a story asynchronously
    
    Args:
        story_id: ID of the story to delete
        no_retry: If True, disables retry behavior
        
    Returns:
        Dictionary with deletion confirmation
    """
    try:
        db: Session = next(get_db())
        try:
            # Get existing story
            story = db.query(Story).filter(Story.id == story_id).first()
            if not story:
                raise ValueError(f"Story with id {story_id} not found")
            
            # Store story info before deletion
            story_info = {
                "id": story.id,
                "title": story.title,
                "deleted": True
            }
            
            # Delete the story
            db.delete(story)
            db.commit()
            
            return story_info
            
        finally:
            db.close()
            
    except Exception as exc:
        if not no_retry:
            self.retry(countdown=60, max_retries=3, exc=exc)
        else:
            raise exc


@celery_app.task(bind=True, name="stories.patch_story")
def patch_story_task(self, story_id: int, patch_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Partially update a story asynchronously
    
    Args:
        story_id: ID of the story to patch
        patch_data: Dictionary containing partial update data
        
    Returns:
        Dictionary with updated story data
    """
    try:
        db: Session = next(get_db())
        try:
            # Get existing story
            story = db.query(Story).filter(Story.id == story_id).first()
            if not story:
                raise ValueError(f"Story with id {story_id} not found")
            
            # Apply patch data directly
            for field, value in patch_data.items():
                if hasattr(story, field):
                    setattr(story, field, value)
            
            db.commit()
            db.refresh(story)
            
            return {
                "id": story.id,
                "title": story.title,
                "content": story.content,
                "author": story.author,
                "genre": story.genre,
                "is_published": story.is_published,
                "created_at": story.created_at.isoformat() if story.created_at else None,
                "updated_at": story.updated_at.isoformat() if story.updated_at else None
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        self.retry(countdown=60, max_retries=3, exc=exc)
