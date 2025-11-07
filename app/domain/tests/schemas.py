from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.domain.questions.schemas import QuestionResponse

class TestCreate(BaseModel):
    exam_type_id: int  # NECO, WAEC, JAMB, NABTEB
    subject_id: int    # Mathematics, English, etc.
    duration_minutes: int
    question_count: int

class TestUpdate(BaseModel):
    exam_type_id: Optional[int] = None
    subject_id: Optional[int] = None
    duration_minutes: Optional[int] = None
    question_count: Optional[int] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class TestResponse(BaseModel):
    id: int
    title: str
    exam_type_id: int
    subject_id: int
    duration_minutes: int
    question_count: int
    total_marks: int
    passing_marks: int
    is_active: bool
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TestWithQuestions(TestResponse):
    questions: List['QuestionResponse'] = []
    
    class Config:
        from_attributes = True