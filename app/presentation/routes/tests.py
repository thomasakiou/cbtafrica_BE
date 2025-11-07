from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.infrastructure.database.connection import get_db
from app.application.handlers.test_handlers import TestHandler
from app.application.commands.test_commands import CreateTestCommand, UpdateTestCommand, DeleteTestCommand
from app.domain.tests.schemas import TestCreate, TestUpdate, TestResponse, TestWithQuestions
from app.infrastructure.auth import get_current_user
from app.infrastructure.database.models import User

router = APIRouter()

@router.post("/", response_model=TestResponse)
def create_test(test: TestCreate, created_by: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = TestHandler(db)
    try:
        command = CreateTestCommand(test_data=test, created_by=created_by)
        return handler.create_test(command)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TestResponse])
def get_tests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = TestHandler(db)
    return handler.get_all_tests(skip=skip, limit=limit)

@router.get("/{test_id}", response_model=TestResponse)
def get_test(test_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = TestHandler(db)
    try:
        return handler.get_test_by_id(test_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Test not found")

@router.get("/{test_id}/with-questions", response_model=TestWithQuestions)
def get_test_with_questions(test_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = TestHandler(db)
    try:
        return handler.get_test_with_questions(test_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Test not found")

@router.get("/exam-type/{exam_type_id}", response_model=List[TestResponse])
def get_tests_by_exam_type(exam_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = TestHandler(db)
    return handler.get_tests_by_exam_type(exam_type_id)

@router.get("/subject/{subject_id}", response_model=List[TestResponse])
def get_tests_by_subject(subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = TestHandler(db)
    return handler.get_tests_by_subject(subject_id)

@router.put("/{test_id}", response_model=TestResponse)
def update_test(test_id: int, test_update: TestUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = TestHandler(db)
    try:
        command = UpdateTestCommand(test_id=test_id, test_data=test_update)
        return handler.update_test(command)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Test not found")

@router.delete("/{test_id}")
def delete_test(test_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = TestHandler(db)
    try:
        command = DeleteTestCommand(test_id=test_id)
        handler.delete_test(command)
        return {"message": "Test deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Test not found")