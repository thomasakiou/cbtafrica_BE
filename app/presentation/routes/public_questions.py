from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import PublicQuestion
from app.domain.public_questions import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.PublicQuestionResponse])
def get_public_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all public questions
    """
    questions = db.query(PublicQuestion).offset(skip).limit(limit).all()
    return questions

@router.post("/", response_model=schemas.PublicQuestionResponse, status_code=status.HTTP_201_CREATED)
def create_public_question(question: schemas.PublicQuestionCreate, db: Session = Depends(get_db)):
    """
    Create a new public question
    """
    db_question = PublicQuestion(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question
