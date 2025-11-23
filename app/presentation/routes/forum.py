from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.infrastructure.database.connection import get_db
from app.application.handlers.forum_handlers import ForumHandler
from app.application.commands.forum_commands import (
    CreateForumPostCommand, ListForumPostsCommand, LikeForumPostCommand,
    CreateForumReplyCommand, ListForumRepliesCommand
)
from app.domain.forum.schemas import ForumPostCreate, ForumPostListResponse, ForumLikeResponse, ForumReplyCreate, ForumReplyResponse
from app.infrastructure.auth import get_current_user
import os
import shutil
import uuid

router = APIRouter()

UPLOAD_DIR = "uploads/forum_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/posts", response_model=ForumPostListResponse)
def get_forum_posts(
    subject: str,
    page: int = 1,
    limit: int = 5,
    sort: str = "newest",
    db: Session = Depends(get_db)
):
    if not subject:
        raise HTTPException(status_code=400, detail="Subject is required")
    handler = ForumHandler(db)
    command = ListForumPostsCommand(subject=subject, page=page, limit=limit, sort=sort)
    return handler.list_posts(command)

@router.post("/posts", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_forum_post(
    title: str = Form(...),
    content: str = Form(...),
    subject: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    image_url = None
    # Accept both None and empty string for image (Swagger UI quirk)
    if image and hasattr(image, "filename") and image.filename:
        ext = os.path.splitext(image.filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            raise HTTPException(status_code=400, detail="Invalid image format")
        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/cbt/{UPLOAD_DIR}/{filename}"
    handler = ForumHandler(db)
    command = CreateForumPostCommand(
        title=title,
        content=content,
        subject=subject,
        image_url=image_url,
        author_id=current_user.id
    )
    post = handler.create_post(command)
    return {"id": post.id, "message": "Post created successfully"}


@router.post("/posts/{post_id}/like", response_model=ForumLikeResponse)
def like_forum_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    handler = ForumHandler(db)
    command = LikeForumPostCommand(post_id=post_id, user_id=current_user.id)
    try:
        return handler.like_post(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Replies endpoints
@router.post("/posts/{post_id}/replies", response_model=ForumReplyResponse, status_code=status.HTTP_201_CREATED)
def create_forum_reply(
    post_id: int,
    body: ForumReplyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    handler = ForumHandler(db)
    command = CreateForumReplyCommand(post_id=post_id, user_id=current_user.id, content=body.content)
    try:
        return handler.create_reply(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/posts/{post_id}/replies", response_model=list[ForumReplyResponse])
def list_forum_replies(
    post_id: int,
    db: Session = Depends(get_db)
):
    handler = ForumHandler(db)
    command = ListForumRepliesCommand(post_id=post_id)
    return handler.list_replies(command)


# @router.get("/debug")
# def debug_route():
#     return {"status": "router working"}
