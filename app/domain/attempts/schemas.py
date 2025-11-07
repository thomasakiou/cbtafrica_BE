from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class AttemptBase(BaseModel):
    test_id: int

class AttemptCreate(AttemptBase):
    pass

class AttemptResponse(BaseModel):
    id: int
    user_id: int
    test_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    score: Optional[float] = None
    percentage: Optional[float] = None
    passed: Optional[bool] = None
    
    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: str
    time_spent: Optional[int] = None

class AttemptSubmit(BaseModel):
    attempt_id: int
    answers: List[AnswerSubmit]