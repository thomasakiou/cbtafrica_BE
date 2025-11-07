from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import ExamType, User
from app.domain.exam_types.schemas import ExamTypeCreate, ExamTypeUpdate, ExamTypeResponse
from app.infrastructure.auth import require_admin, get_current_user
from app.application.handlers.exam_type_handlers import ExamTypeHandler
from app.application.commands.exam_type_commands import CreateExamTypeCommand, UpdateExamTypeCommand, DeleteExamTypeCommand

router = APIRouter()

@router.post("/", response_model=ExamTypeResponse)
def create_exam_type(exam_type: ExamTypeCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    handler = ExamTypeHandler(db)
    try:
        command = CreateExamTypeCommand(exam_type_data=exam_type)
        return handler.create_exam_type(command)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ExamTypeResponse])
def get_exam_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = ExamTypeHandler(db)
    return handler.get_all_exam_types(skip=skip, limit=limit)

@router.get("/{exam_type_id}", response_model=ExamTypeResponse)
def get_exam_type(exam_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = ExamTypeHandler(db)
    try:
        return handler.get_exam_type_by_id(exam_type_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Exam type not found")

@router.put("/{exam_type_id}", response_model=ExamTypeResponse)
def update_exam_type(exam_type_id: int, exam_type_update: ExamTypeUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    handler = ExamTypeHandler(db)
    try:
        command = UpdateExamTypeCommand(exam_type_id=exam_type_id, exam_type_data=exam_type_update)
        return handler.update_exam_type(command)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Exam type not found")

@router.delete("/{exam_type_id}")
def delete_exam_type(exam_type_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    handler = ExamTypeHandler(db)
    try:
        command = DeleteExamTypeCommand(exam_type_id=exam_type_id)
        handler.delete_exam_type(command)
        return {"message": "Exam type deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Exam type not found")