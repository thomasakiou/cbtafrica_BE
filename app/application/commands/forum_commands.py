from pydantic import BaseModel
from typing import Optional

class CreateForumPostCommand(BaseModel):
    title: str
    content: str
    subject: str
    image_url: Optional[str] = None
    author_id: int

class ListForumPostsCommand(BaseModel):
    subject: str
    page: int = 1
    limit: int = 10
    sort: str = "newest"  # or "popular"

class LikeForumPostCommand(BaseModel):
    post_id: int
    user_id: int


# ForumReply commands
class CreateForumReplyCommand(BaseModel):
    post_id: int
    user_id: int
    content: str

class ListForumRepliesCommand(BaseModel):
    post_id: int
