from pydantic import BaseModel
from app.domain.tests.schemas import TestCreate, TestUpdate

class CreateTestCommand(BaseModel):
    test_data: TestCreate
    created_by: int

class UpdateTestCommand(BaseModel):
    test_id: int
    test_data: TestUpdate

class DeleteTestCommand(BaseModel):
    test_id: int

class GetTestCommand(BaseModel):
    test_id: int

class GetTestsCommand(BaseModel):
    skip: int = 0
    limit: int = 100

class GetTestsByExamTypeCommand(BaseModel):
    exam_type_id: int

class GetTestsBySubjectCommand(BaseModel):
    subject_id: int

class ActivateTestCommand(BaseModel):
    test_id: int
    is_active: bool