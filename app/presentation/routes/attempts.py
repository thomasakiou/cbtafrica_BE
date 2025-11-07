from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.infrastructure.database.connection import get_db
from app.application.handlers.attempt_handlers import AttemptHandler
from app.domain.attempts.schemas import AttemptCreate, AttemptResponse, AttemptSubmit
from app.domain.results.schemas import ResultResponse
from app.infrastructure.auth import get_current_user
from app.infrastructure.database.models import User

router = APIRouter()

@router.post("/start", response_model=AttemptResponse)
def start_attempt(user_id: int, attempt_data: AttemptCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = AttemptHandler(db)
    try:
        return handler.start_attempt(user_id, attempt_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/submit", response_model=ResultResponse)
def submit_attempt(submission: AttemptSubmit, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = AttemptHandler(db)
    try:
        return handler.submit_attempt(submission)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=List[AttemptResponse])
def get_user_attempts(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = AttemptHandler(db)
    return handler.get_user_attempts(user_id)

@router.get("/{attempt_id}", response_model=AttemptResponse)
def get_attempt(attempt_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    handler = AttemptHandler(db)
    try:
        return handler.get_attempt_by_id(attempt_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Attempt not found")