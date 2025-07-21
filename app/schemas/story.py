from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    genre: Optional[str] = Field(None, max_length=50)
    is_published: bool = False


class StoryCreate(StoryBase):
    pass


class StoryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    genre: Optional[str] = Field(None, max_length=50)
    is_published: Optional[bool] = None


class StoryResponse(StoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
