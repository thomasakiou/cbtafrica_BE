from pydantic import BaseModel
from app.domain.subjects.schemas import SubjectCreate, SubjectUpdate

class CreateSubjectCommand(BaseModel):
    subject_data: SubjectCreate

class UpdateSubjectCommand(BaseModel):
    subject_id: int
    subject_data: SubjectUpdate

class DeleteSubjectCommand(BaseModel):
    subject_id: int