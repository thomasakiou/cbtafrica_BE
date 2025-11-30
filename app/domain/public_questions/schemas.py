from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PublicQuestionBase(BaseModel):
    subject: str
    question: str
    solution: str

class PublicQuestionCreate(PublicQuestionBase):
    pass

class PublicQuestionResponse(PublicQuestionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
