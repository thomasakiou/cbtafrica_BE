from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List

class AttemptBase(BaseModel):
    test_id: int

class AttemptCreate(AttemptBase):
    pass

class TestResponse(BaseModel):
    id: int
    title: str
    subject: str
    total_marks: int
    passing_marks: int

    class Config:
        from_attributes = True
    
    @field_validator('subject', mode='before')
    def extract_subject_name(cls, v):
        if hasattr(v, 'name'):
            return v.name
        return v

class AttemptResponse(BaseModel):
    id: int
    user_id: int
    test_id: Optional[int] = None
    subject_id: Optional[int] = None
    exam_type_id: Optional[int] = None
    is_practice: Optional[bool] = False
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    score: Optional[float] = None
    percentage: Optional[float] = None
    passed: Optional[bool] = None
    time_taken: Optional[int] = None
    test: Optional[TestResponse] = None
    
    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: str
    time_spent: Optional[int] = None

class AttemptSubmit(BaseModel):
    attempt_id: int
    answers: List[AnswerSubmit]

class PracticeAttemptAnswer(BaseModel):
    question_id: int
    answer_text: str
    is_correct: bool

class PracticeAttemptCreate(BaseModel):
    user_id: int
    subject_id: int
    exam_type_id: int
    score: float
    total_questions: int
    time_spent: int
    answers: List[PracticeAttemptAnswer]

class LeaderboardEntry(BaseModel):
    user_id: int
    full_name: Optional[str] = None
    username: Optional[str] = None
    score: float
    test_title: Optional[str] = None
    subject_name: Optional[str] = None
    date: datetime
    is_practice: bool