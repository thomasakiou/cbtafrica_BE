"""
News Routes - API endpoints for news management

This module handles all news-related operations including:
- Creating news items (admin only)
- Retrieving news items (public endpoint)
- Updating news items (admin only)
- Deleting news items (admin only)

Follows Domain-Driven Design (DDD) pattern with:
- Routes handle HTTP requests/responses
- Commands encapsulate business operations
- Handlers contain business logic
- Models represent database entities
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.database.connection import get_db
from app.application.handlers.news_handlers import NewsHandler
from app.application.commands.news_commands import (
    CreateNewsCommand,
    UpdateNewsCommand,
    DeleteNewsCommand,
    GetNewsCommand,
    ListNewsCommand
)
from app.domain.news.schemas import NewsCreate, NewsUpdate, NewsResponse
from app.infrastructure.auth import get_current_user, require_admin

# Create router for news endpoints
router = APIRouter()


@router.post("/", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
def create_news(
    news: NewsCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Create a new news item (Admin only)
    
    Args:
        news: NewsCreate schema with title, content, url, date
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        NewsResponse with created news item data
        
    Raises:
        HTTPException 400: If news creation fails
        HTTPException 401: If user not authenticated
        HTTPException 403: If user is not admin
    """
    try:
        handler = NewsHandler(db)
        command = CreateNewsCommand(news_data=news)
        return handler.create_news(command)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[NewsResponse])
def list_news(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of news items (Public endpoint)
    
    News items are ordered by date (newest first).
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (max 100)
        db: Database session
        
    Returns:
        List of NewsResponse objects
    """
    try:
        handler = NewsHandler(db)
        command = ListNewsCommand(skip=skip, limit=min(limit, 100))
        return handler.list_news(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{news_id}", response_model=NewsResponse)
def get_news(
    news_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a single news item by ID (Public endpoint)
    
    Args:
        news_id: ID of the news item to retrieve
        db: Database session
        
    Returns:
        NewsResponse with news item data
        
    Raises:
        HTTPException 404: If news item not found
    """
    try:
        handler = NewsHandler(db)
        command = GetNewsCommand(news_id=news_id)
        return handler.get_news_by_id(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: int,
    news: NewsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Update an existing news item (Admin only)
    
    Args:
        news_id: ID of the news item to update
        news: NewsUpdate schema with fields to update
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        NewsResponse with updated news item data
        
    Raises:
        HTTPException 404: If news item not found
        HTTPException 400: If update fails
        HTTPException 401: If user not authenticated
        HTTPException 403: If user is not admin
    """
    try:
        handler = NewsHandler(db)
        command = UpdateNewsCommand(news_id=news_id, news_data=news)
        return handler.update_news(command)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Delete a news item (Admin only)
    
    Args:
        news_id: ID of the news item to delete
        db: Database session
        current_user: Current authenticated admin user
        
    Raises:
        HTTPException 404: If news item not found
        HTTPException 400: If deletion fails
        HTTPException 401: If user not authenticated
        HTTPException 403: If user is not admin
    """
    try:
        handler = NewsHandler(db)
        command = DeleteNewsCommand(news_id=news_id)
        handler.delete_news(command)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
