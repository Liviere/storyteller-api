from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.story import Story
from app.schemas.story import StoryCreate, StoryResponse, StoryUpdate
from app.schemas.async_responses import TaskResponse
from app.services.task_service import get_task_service, TaskService

router = APIRouter()


@router.post("/stories/", response_model=TaskResponse)
async def create_story(
    story: StoryCreate, 
    task_service: TaskService = Depends(get_task_service)
):
    """Create a new story asynchronously"""
    try:
        story_data = story.model_dump()
        task_id = task_service.create_story_async(story_data)
        
        return TaskResponse(
            task_id=task_id,
            status="PENDING",
            message="Story creation task submitted successfully",
            estimated_time=30
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit story creation task: {str(e)}"
        )


@router.get("/stories/", response_model=List[StoryResponse])
async def get_stories(
    skip: int = Query(0, ge=0, description="Number of stories to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of stories to return"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    author: Optional[str] = Query(None, description="Filter by author"),
    published_only: bool = Query(False, description="Show only published stories"),
    db: Session = Depends(get_db),
):
    """Get all stories with optional filtering"""
    query = db.query(Story)

    if genre:
        query = query.filter(Story.genre == genre)
    if author:
        query = query.filter(Story.author.ilike(f"%{author}%"))
    if published_only:
        query = query.filter(Story.is_published == True)

    stories = query.offset(skip).limit(limit).all()
    return stories


@router.get("/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: int, db: Session = Depends(get_db)):
    """Get a specific story by ID"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@router.put("/stories/{story_id}", response_model=TaskResponse)
async def update_story(
    story_id: int, 
    story_update: StoryUpdate, 
    task_service: TaskService = Depends(get_task_service)
):
    """Update a specific story asynchronously"""
    try:
        story_data = story_update.model_dump(exclude_unset=True)
        task_id = task_service.update_story_async(story_id, story_data)
        
        return TaskResponse(
            task_id=task_id,
            status="PENDING",
            message="Story update task submitted successfully",
            estimated_time=20
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit story update task: {str(e)}"
        )


@router.delete("/stories/{story_id}", response_model=TaskResponse)
async def delete_story(
    story_id: int, 
    task_service: TaskService = Depends(get_task_service)
):
    """Delete a specific story asynchronously"""
    try:
        task_id = task_service.delete_story_async(story_id)
        
        return TaskResponse(
            task_id=task_id,
            status="PENDING",
            message="Story deletion task submitted successfully",
            estimated_time=15
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit story deletion task: {str(e)}"
        )


@router.patch("/stories/{story_id}/publish", response_model=TaskResponse)
async def publish_story(
    story_id: int, 
    task_service: TaskService = Depends(get_task_service)
):
    """Publish a story asynchronously"""
    try:
        patch_data = {"is_published": True}
        task_id = task_service.patch_story_async(story_id, patch_data)
        
        return TaskResponse(
            task_id=task_id,
            status="PENDING",
            message="Story publish task submitted successfully",
            estimated_time=10
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit story publish task: {str(e)}"
        )


@router.patch("/stories/{story_id}/unpublish", response_model=TaskResponse)
async def unpublish_story(
    story_id: int, 
    task_service: TaskService = Depends(get_task_service)
):
    """Unpublish a story asynchronously"""
    try:
        patch_data = {"is_published": False}
        task_id = task_service.patch_story_async(story_id, patch_data)
        
        return TaskResponse(
            task_id=task_id,
            status="PENDING",
            message="Story unpublish task submitted successfully",
            estimated_time=10
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit story unpublish task: {str(e)}"
        )
