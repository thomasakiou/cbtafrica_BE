from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExamTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class ExamTypeCreate(ExamTypeBase):
    pass

class ExamTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ExamTypeResponse(ExamTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True