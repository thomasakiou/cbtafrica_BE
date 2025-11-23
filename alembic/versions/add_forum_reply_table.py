"""add_forum_reply_table

Revision ID: add_forum_reply_table
Revises: 433b9e19eaab
Create Date: 2025-11-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_forum_reply_table'
down_revision: Union[str, None] = '433b9e19eaab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'forum_replies',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('post_id', sa.UUID(), sa.ForeignKey('forum_posts.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('forum_replies')
