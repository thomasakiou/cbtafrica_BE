from pydantic import BaseModel
from app.domain.questions.schemas import QuestionCreate, QuestionUpdate
from typing import List, Optional

class CreateQuestionCommand(BaseModel):
    question_data: QuestionCreate

class CreateBulkQuestionsCommand(BaseModel):
    questions: List[QuestionCreate]

class UpdateQuestionCommand(BaseModel):
    question_id: int
    question_data: QuestionUpdate

class DeleteQuestionCommand(BaseModel):
    question_id: int

class GetQuestionCommand(BaseModel):
    question_id: int

class GetQuestionsByExamTypeAndSubjectCommand(BaseModel):
    exam_type_id: int
    subject_id: int

class GetQuestionsByExamTypeCommand(BaseModel):
    exam_type_id: int

class GetQuestionsBySubjectCommand(BaseModel):
    subject_id: int

class GetQuestionsCommand(BaseModel):
    exam_type_id: Optional[int] = None
    subject_id: Optional[int] = None
    skip: int = 0
    limit: int = 100