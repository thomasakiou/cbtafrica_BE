from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.infrastructure.database.models import ForumPost, ForumLike, ForumReply, User
from app.application.commands.forum_commands import (
    CreateForumPostCommand, ListForumPostsCommand, LikeForumPostCommand,
    CreateForumReplyCommand, ListForumRepliesCommand
)
from app.domain.forum.schemas import ForumPostResponse, ForumPostListResponse, ForumLikeResponse, ForumAuthor, ForumReplyResponse
from datetime import datetime
from typing import List

class ForumHandler:
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, command: CreateForumPostCommand) -> ForumPostResponse:
        post = ForumPost(
            title=command.title,
            content=command.content,
            subject=command.subject,
            image_url=command.image_url,
            author_id=command.author_id
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return self._to_post_response(post)

    def list_posts(self, command: ListForumPostsCommand) -> ForumPostListResponse:
        query = self.db.query(ForumPost).filter(ForumPost.subject == command.subject)
        if command.sort == "popular":
            query = query.outerjoin(ForumLike).group_by(ForumPost.id).order_by(desc(func.count(ForumLike.id)), desc(ForumPost.created_at))
        else:
            query = query.order_by(desc(ForumPost.created_at))
        total_posts = query.count()
        total_pages = (total_posts + command.limit - 1) // command.limit
        posts = query.offset((command.page - 1) * command.limit).limit(command.limit).all()
        return ForumPostListResponse(
            posts=[self._to_post_response(post) for post in posts],
            totalPages=total_pages,
            currentPage=command.page
        )

    def like_post(self, command: LikeForumPostCommand) -> ForumLikeResponse:
        post = self.db.query(ForumPost).filter(ForumPost.id == command.post_id).first()
        if not post:
            raise ValueError("Post not found")
        like = self.db.query(ForumLike).filter(ForumLike.post_id == command.post_id, ForumLike.user_id == command.user_id).first()
        if like:
            self.db.delete(like)
            self.db.commit()
            message = "Post unliked"
        else:
            like = ForumLike(post_id=command.post_id, user_id=command.user_id)
            self.db.add(like)
            self.db.commit()
            message = "Post liked"
        likes_count = self.db.query(ForumLike).filter(ForumLike.post_id == command.post_id).count()
        return ForumLikeResponse(postId=str(command.post_id), likes=likes_count, message=message)

    def _to_post_response(self, post: ForumPost) -> ForumPostResponse:
        author = self.db.query(User).filter(User.id == post.author_id).first()
        likes_count = self.db.query(ForumLike).filter(ForumLike.post_id == post.id).count()
        replies = self.db.query(ForumReply).filter(ForumReply.post_id == post.id).order_by(ForumReply.created_at.asc()).all()
        reply_objs = [self._to_reply_response(reply) for reply in replies]
        return ForumPostResponse(
            id=int(post.id),
            title=post.title,
            content=post.content,
            subject=post.subject,
            imageUrl=post.image_url,
            likes=likes_count,
            replyCount=len(reply_objs),
            replies=reply_objs,
            author=ForumAuthor(
                id=str(author.id),
                name=author.full_name or author.username,
                avatar=None  # Add avatar logic if available
            ),
            createdAt=post.created_at,
            updatedAt=post.updated_at
        )

    def _to_reply_response(self, reply: ForumReply) -> ForumReplyResponse:
        user = self.db.query(User).filter(User.id == reply.user_id).first()
        return ForumReplyResponse(
            id=reply.id,
            postId=int(reply.post_id),
            user=ForumAuthor(
                id=int(user.id),
                name=user.full_name or user.username,
                avatar=None
            ),
            content=reply.content,
            createdAt=reply.created_at,
            updatedAt=reply.updated_at
        )

    def create_reply(self, command: CreateForumReplyCommand) -> ForumReplyResponse:
        post = self.db.query(ForumPost).filter(ForumPost.id == command.post_id).first()
        if not post:
            raise ValueError("Post not found")
        reply = ForumReply(
            post_id=command.post_id,
            user_id=command.user_id,
            content=command.content
        )
        self.db.add(reply)
        self.db.commit()
        self.db.refresh(reply)
        return self._to_reply_response(reply)

    def list_replies(self, command: ListForumRepliesCommand) -> list:
        replies = self.db.query(ForumReply).filter(ForumReply.post_id == command.post_id).order_by(ForumReply.created_at.asc()).all()
        return [self._to_reply_response(reply) for reply in replies]
