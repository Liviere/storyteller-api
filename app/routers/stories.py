from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.story import Story
from app.schemas.story import StoryCreate, StoryResponse, StoryUpdate

router = APIRouter()


@router.post("/stories/", response_model=StoryResponse)
async def create_story(story: StoryCreate, db: Session = Depends(get_db)):
    """Create a new story"""
    db_story = Story(**story.dict())
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story


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


@router.put("/stories/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: int, story_update: StoryUpdate, db: Session = Depends(get_db)
):
    """Update a specific story"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    update_data = story_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(story, field, value)

    db.commit()
    db.refresh(story)
    return story


@router.delete("/stories/{story_id}")
async def delete_story(story_id: int, db: Session = Depends(get_db)):
    """Delete a specific story"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    db.delete(story)
    db.commit()
    return {"message": "Story deleted successfully"}


@router.patch("/stories/{story_id}/publish")
async def publish_story(story_id: int, db: Session = Depends(get_db)):
    """Publish a story"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    story.is_published = True
    db.commit()
    db.refresh(story)
    return {"message": "Story published successfully", "story": story}


@router.patch("/stories/{story_id}/unpublish")
async def unpublish_story(story_id: int, db: Session = Depends(get_db)):
    """Unpublish a story"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    story.is_published = False
    db.commit()
    db.refresh(story)
    return {"message": "Story unpublished successfully", "story": story}
