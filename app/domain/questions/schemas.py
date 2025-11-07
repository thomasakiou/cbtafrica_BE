from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class QuestionBase(BaseModel):
    question_text: str
    question_type: str
    options: Optional[Dict[str, Any]] = None
    correct_answer: str
    explanation: Optional[str] = None

    class Config:
        from_attributes = True

class QuestionCreate(QuestionBase):
    exam_type_id: int  # NECO, WAEC, JAMB, NABTEB
    subject_id: int    # Mathematics, English, etc.

    class Config:
        from_attributes = True

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True

class QuestionResponse(QuestionBase):
    id: int
    exam_type_id: int
    subject_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuestionForTest(BaseModel):
    id: int
    question_text: str
    question_type: str
    options: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True