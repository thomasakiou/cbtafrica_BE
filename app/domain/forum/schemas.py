from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

class ForumAuthor(BaseModel):
    id: int
    name: str
    avatar: Optional[HttpUrl] = None

    class Config:
        from_attributes = True

class ForumPostCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)

    class Config:
        from_attributes = True

class ForumPostResponse(BaseModel):
    id: int
    title: str
    content: str
    subject: str
    imageUrl: Optional[HttpUrl] = None
    likes: int
    replyCount: int
    replies: Optional[List["ForumReplyResponse"]] = None
    author: ForumAuthor
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ForumPostListResponse(BaseModel):
    posts: List[ForumPostResponse]
    totalPages: int
    currentPage: int

    class Config:
        from_attributes = True


# ForumReply schemas
class ForumReplyCreate(BaseModel):
    content: str = Field(..., min_length=1)

    class Config:
        from_attributes = True


class ForumReplyResponse(BaseModel):
    id: int
    postId: int
    user: ForumAuthor
    content: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ForumLikeResponse(BaseModel):
    postId: int
    likes: int
    message: str

    class Config:
        from_attributes = True


# ForumPostResponse.update_forward_refs()
