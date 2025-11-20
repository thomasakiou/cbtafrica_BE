from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional


class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="The news heading")
    content: str = Field(..., min_length=1, description="Short description of the news")
    url: HttpUrl = Field(..., description="URL to the actual news page on the internet")
    date: datetime = Field(..., description="Date the news was published")


class NewsCreate(NewsBase):
    """Schema for creating a new news item"""
    pass


class NewsUpdate(BaseModel):
    """Schema for updating an existing news item - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    url: Optional[HttpUrl] = None
    date: Optional[datetime] = None


class NewsResponse(NewsBase):
    """Schema for news item response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
