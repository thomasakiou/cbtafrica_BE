from sqlalchemy.orm import Session
from app.infrastructure.database.models import Test, Question, ExamType, Subject
from app.application.commands.test_commands import *
from app.domain.tests.schemas import TestResponse, TestWithQuestions
from app.domain.questions.schemas import QuestionResponse
from typing import List
import random

class TestHandler:
    def __init__(self, db: Session):
        self.db = db
    
    def create_test(self, command: CreateTestCommand) -> TestResponse:
        # Generate test title
        exam_type = self.db.query(ExamType).filter(ExamType.id == command.test_data.exam_type_id).first()
        subject = self.db.query(Subject).filter(Subject.id == command.test_data.subject_id).first()
        title = f"{exam_type.name} {subject.name} Test"
        
        # Calculate marks (1 mark per question)
        total_marks = command.test_data.question_count
        passing_marks = int(total_marks * 0.5)  # 50% to pass
        
        db_test = Test(
            title=title,
            exam_type_id=command.test_data.exam_type_id,
            subject_id=command.test_data.subject_id,
            duration_minutes=command.test_data.duration_minutes,
            question_count=command.test_data.question_count,
            total_marks=total_marks,
            passing_marks=passing_marks,
            created_by=command.created_by
        )
        self.db.add(db_test)
        self.db.commit()
        self.db.refresh(db_test)
        return TestResponse.model_validate(db_test)
    
    def get_all_tests(self, command: GetTestsCommand) -> List[TestResponse]:
        tests = self.db.query(Test).offset(command.skip).limit(command.limit).all()
        return [TestResponse.model_validate(t) for t in tests]
    
    def get_test_by_id(self, command: GetTestCommand) -> TestResponse:
        test = self.db.query(Test).filter(Test.id == command.test_id).first()
        if not test:
            raise ValueError("Test not found")
        return TestResponse.model_validate(test)
    
    def get_test_with_questions(self, test_id: int) -> TestWithQuestions:
        test = self.db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise ValueError("Test not found")
        
        # Get random questions for this test
        available_questions = self.db.query(Question).filter(
            Question.exam_type_id == test.exam_type_id,
            Question.subject_id == test.subject_id
        ).all()
        
        selected_questions = random.sample(available_questions, min(test.question_count, len(available_questions)))
        
        test_response = TestResponse.model_validate(test)
        return TestWithQuestions(
            **test_response.model_dump(),
            questions=[QuestionResponse.model_validate(q) for q in selected_questions]
        )
    
    def get_tests_by_exam_type(self, command: GetTestsByExamTypeCommand) -> List[TestResponse]:
        tests = self.db.query(Test).filter(Test.exam_type_id == command.exam_type_id).all()
        return [TestResponse.model_validate(t) for t in tests]
    
    def get_tests_by_subject(self, command: GetTestsBySubjectCommand) -> List[TestResponse]:
        tests = self.db.query(Test).filter(Test.subject_id == command.subject_id).all()
        return [TestResponse.model_validate(t) for t in tests]
    
    def update_test(self, command: UpdateTestCommand) -> TestResponse:
        test = self.db.query(Test).filter(Test.id == command.test_id).first()
        if not test:
            raise ValueError("Test not found")
        
        for field, value in command.test_data.model_dump(exclude_unset=True).items():
            setattr(test, field, value)
        
        self.db.commit()
        self.db.refresh(test)
        return TestResponse.model_validate(test)
    
    def delete_test(self, command: DeleteTestCommand) -> bool:
        test = self.db.query(Test).filter(Test.id == command.test_id).first()
        if not test:
            raise ValueError("Test not found")
        
        self.db.delete(test)
        self.db.commit()
        return True