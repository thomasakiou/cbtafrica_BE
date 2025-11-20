from sqlalchemy.orm import Session
from datetime import datetime
from app.infrastructure.database.models import News
from app.application.commands.news_commands import (
    CreateNewsCommand,
    UpdateNewsCommand,
    DeleteNewsCommand,
    GetNewsCommand,
    ListNewsCommand
)
from app.domain.news.schemas import NewsResponse


class NewsHandler:
    """Handler for news-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_news(self, command: CreateNewsCommand) -> NewsResponse:
        """
        Create a new news item
        
        Args:
            command: CreateNewsCommand containing news data
            
        Returns:
            NewsResponse with created news item data
            
        Raises:
            ValueError: If news creation fails
        """
        try:
            db_news = News(
                title=command.news_data.title,
                content=command.news_data.content,
                url=str(command.news_data.url),
                date=command.news_data.date
            )
            self.db.add(db_news)
            self.db.commit()
            self.db.refresh(db_news)
            return NewsResponse.model_validate(db_news)
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create news item: {str(e)}")
    
    def get_news_by_id(self, command: GetNewsCommand) -> NewsResponse:
        """
        Retrieve a single news item by ID
        
        Args:
            command: GetNewsCommand containing news_id
            
        Returns:
            NewsResponse with news item data
            
        Raises:
            ValueError: If news item not found
        """
        news = self.db.query(News).filter(News.id == command.news_id).first()
        if not news:
            raise ValueError(f"News item with ID {command.news_id} not found")
        return NewsResponse.model_validate(news)
    
    def list_news(self, command: ListNewsCommand) -> list[NewsResponse]:
        """
        Retrieve a list of news items with pagination, ordered by date (newest first)
        
        Args:
            command: ListNewsCommand with skip and limit parameters
            
        Returns:
            List of NewsResponse objects
        """
        news_items = (
            self.db.query(News)
            .order_by(News.date.desc())
            .offset(command.skip)
            .limit(command.limit)
            .all()
        )
        return [NewsResponse.model_validate(news) for news in news_items]
    
    def update_news(self, command: UpdateNewsCommand) -> NewsResponse:
        """
        Update an existing news item
        
        Args:
            command: UpdateNewsCommand containing news_id and update data
            
        Returns:
            NewsResponse with updated news item data
            
        Raises:
            ValueError: If news item not found
        """
        news = self.db.query(News).filter(News.id == command.news_id).first()
        if not news:
            raise ValueError(f"News item with ID {command.news_id} not found")
        
        # Update only provided fields
        update_data = command.news_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "url" and value is not None:
                setattr(news, field, str(value))
            else:
                setattr(news, field, value)
        
        news.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(news)
            return NewsResponse.model_validate(news)
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to update news item: {str(e)}")
    
    def delete_news(self, command: DeleteNewsCommand) -> None:
        """
        Delete a news item
        
        Args:
            command: DeleteNewsCommand containing news_id
            
        Raises:
            ValueError: If news item not found
        """
        news = self.db.query(News).filter(News.id == command.news_id).first()
        if not news:
            raise ValueError(f"News item with ID {command.news_id} not found")
        
        try:
            self.db.delete(news)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to delete news item: {str(e)}")
