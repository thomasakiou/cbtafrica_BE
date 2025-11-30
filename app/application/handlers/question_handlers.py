from sqlalchemy.orm import Session
from app.infrastructure.database.models import Question
from app.application.commands.question_commands import *
from app.domain.questions.schemas import QuestionResponse
from typing import List

class QuestionHandler:
    def __init__(self, db: Session):
        self.db = db
    
    def create_question(self, command: CreateQuestionCommand) -> QuestionResponse:
        db_question = Question(**command.question_data.model_dump())
        self.db.add(db_question)
        self.db.commit()
        self.db.refresh(db_question)
        return QuestionResponse.model_validate(db_question)
    
    def create_bulk_questions(self, command: CreateBulkQuestionsCommand) -> List[QuestionResponse]:
        db_questions = []
        for question_data in command.questions:
            db_question = Question(**question_data.model_dump())
            self.db.add(db_question)
            db_questions.append(db_question)
        
        self.db.commit()
        for q in db_questions:
            self.db.refresh(q)
        
        return [QuestionResponse.model_validate(q) for q in db_questions]
    
    def get_question_by_id(self, command: GetQuestionCommand) -> QuestionResponse:
        question = self.db.query(Question).filter(Question.id == command.question_id).first()
        if not question:
            raise ValueError("Question not found")
        return QuestionResponse.model_validate(question)
    
    def get_questions_by_exam_type_and_subject(self, command: GetQuestionsByExamTypeAndSubjectCommand) -> List[QuestionResponse]:
        query = self.db.query(Question).filter(
            Question.exam_type_id == command.exam_type_id,
            Question.subject_id == command.subject_id
        )
        if command.year is not None:
            query = query.filter(Question.year == command.year)
        questions = query.all()
        return [QuestionResponse.model_validate(q) for q in questions]

    def get_all_questions(self, command: GetQuestionsCommand):
        q = self.db.query(Question)
        if command.exam_type_id:
            q = q.filter(Question.exam_type_id == command.exam_type_id)
        if command.subject_id:
            q = q.filter(Question.subject_id == command.subject_id)
        if command.year is not None:
            q = q.filter(Question.year == command.year)
        return q.offset(command.skip).limit(command.limit).all()


    def get_questions_by_exam_type(self, command: GetQuestionsByExamTypeCommand) -> List[QuestionResponse]:
        query = self.db.query(Question).filter(Question.exam_type_id == command.exam_type_id)
        if command.year is not None:
            query = query.filter(Question.year == command.year)
        questions = query.all()
        return [QuestionResponse.model_validate(q) for q in questions]
    
    def get_questions_by_subject(self, command: GetQuestionsBySubjectCommand) -> List[QuestionResponse]:
        query = self.db.query(Question).filter(Question.subject_id == command.subject_id)
        if command.year is not None:
            query = query.filter(Question.year == command.year)
        questions = query.all()
        return [QuestionResponse.model_validate(q) for q in questions]
    
    def update_question(self, command: UpdateQuestionCommand) -> QuestionResponse:
        question = self.db.query(Question).filter(Question.id == command.question_id).first()
        if not question:
            raise ValueError("Question not found")
        
        for field, value in command.question_data.model_dump(exclude_unset=True).items():
            setattr(question, field, value)
        
        self.db.commit()
        self.db.refresh(question)
        return QuestionResponse.model_validate(question)
    
    def delete_question(self, command: DeleteQuestionCommand) -> bool:
        question = self.db.query(Question).filter(Question.id == command.question_id).first()
        if not question:
            raise ValueError("Question not found")
        
        self.db.delete(question)
        self.db.commit()
        return True
    
    # class GetQuestionsHandler:
    # def __init__(self, db: Session):
    #     self.db = db

