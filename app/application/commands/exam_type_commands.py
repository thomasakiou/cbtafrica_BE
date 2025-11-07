from pydantic import BaseModel
from app.domain.exam_types.schemas import ExamTypeCreate, ExamTypeUpdate

class CreateExamTypeCommand(BaseModel):
    exam_type_data: ExamTypeCreate

class UpdateExamTypeCommand(BaseModel):
    exam_type_id: int
    exam_type_data: ExamTypeUpdate

class DeleteExamTypeCommand(BaseModel):
    exam_type_id: int