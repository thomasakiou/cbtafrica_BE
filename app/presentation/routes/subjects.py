from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import Subject, User
from app.domain.subjects.schemas import SubjectCreate, SubjectUpdate, SubjectResponse
from app.infrastructure.auth import require_admin, get_current_user
from app.application.handlers.subject_handlers import SubjectHandler
from app.application.commands.subject_commands import CreateSubjectCommand, UpdateSubjectCommand, DeleteSubjectCommand

router = APIRouter()

@router.post("/", response_model=SubjectResponse)
def create_subject(subject: SubjectCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    handler = SubjectHandler(db)
    try:
        command = CreateSubjectCommand(subject_data=subject)
        return handler.create_subject(command)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[SubjectResponse])
def get_subjects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = SubjectHandler(db)
    return handler.get_all_subjects()

@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = SubjectHandler(db)
    try:
        return handler.get_subject_by_id(subject_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Subject not found")

@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(subject_id: int, subject_update: SubjectUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    handler = SubjectHandler(db)
    try:
        command = UpdateSubjectCommand(subject_id=subject_id, subject_data=subject_update)
        return handler.update_subject(command)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Subject not found")

@router.delete("/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    handler = SubjectHandler(db)
    try:
        command = DeleteSubjectCommand(subject_id=subject_id)
        handler.delete_subject(command)
        return {"message": "Subject deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Subject not found")