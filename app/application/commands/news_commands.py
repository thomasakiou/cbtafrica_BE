from pydantic import BaseModel
from app.domain.news.schemas import NewsCreate, NewsUpdate


class CreateNewsCommand(BaseModel):
    """Command for creating a new news item"""
    news_data: NewsCreate


class UpdateNewsCommand(BaseModel):
    """Command for updating an existing news item"""
    news_id: int
    news_data: NewsUpdate


class DeleteNewsCommand(BaseModel):
    """Command for deleting a news item"""
    news_id: int


class GetNewsCommand(BaseModel):
    """Command for retrieving a single news item by ID"""
    news_id: int


class ListNewsCommand(BaseModel):
    """Command for retrieving a list of news items with pagination"""
    skip: int = 0
    limit: int = 100
