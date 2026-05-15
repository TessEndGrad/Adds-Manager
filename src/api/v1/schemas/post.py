from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TagOut(BaseModel):
    id:   int
    name: str

    model_config = {"from_attributes": True}


class MediaOut(BaseModel):
    id:         int
    file_url:   str
    media_type: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PostOut(BaseModel):
    id:           int
    title:        Optional[str]      = None
    content:      Optional[str]      = None
    author_id:    int
    post_type_id: Optional[int]      = None
    status_id:    int
    scheduled_at: Optional[datetime] = None
    created_at:   Optional[datetime] = None
    updated_at:   Optional[datetime] = None
    tags:         list[TagOut]       = []
    media:        list[MediaOut]     = []

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    total:     int
    page:      int
    page_size: int
    items:     list[PostOut]