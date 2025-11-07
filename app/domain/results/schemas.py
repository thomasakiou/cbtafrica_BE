from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AnswerResult(BaseModel):
    question_id: int
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    marks_obtained: float
    total_marks: int
    explanation: Optional[str] = None

    class Config:
        from_attributes = True

class ResultResponse(BaseModel):
    attempt_id: int
    user_id: int
    test_id: int
    test_title: str
    start_time: datetime
    end_time: datetime
    total_questions: int
    correct_answers: int
    score: float
    percentage: float
    passed: bool
    answers: List[AnswerResult]

    class Config:
        from_attributes = True
    
class ResultSummary(BaseModel):
    attempt_id: int
    test_title: str
    score: float
    percentage: float
    passed: bool
    completed_at: datetime

    class Config:
        from_attributes = True