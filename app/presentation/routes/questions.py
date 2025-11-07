from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import Question, User
from app.domain.questions.schemas import QuestionCreate, QuestionUpdate, QuestionResponse
from app.infrastructure.auth import require_admin, get_current_user
from app.application.commands.question_commands import GetQuestionsCommand


router = APIRouter()

@router.post("/", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    db_question = Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return QuestionResponse.model_validate(db_question)

# @router.get("/", response_model=List[QuestionResponse])
# def get_questions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     questions = db.query(Question).all()
#     return [QuestionResponse.model_validate(q) for q in questions]  


# @router.get("/")
# async def get_questions(
#     exam_type_id: Optional[int] = Query(None),
#     subject_id: Optional[int] = Query(None),
#     skip: int = Query(0),
#     limit: int = Query(100),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     query = db.query(Question)
#     if exam_type_id:
#         query = query.filter(Question.exam_type_id == exam_type_id)
#     if subject_id:
#         query = query.filter(Question.subject_id == subject_id)
#     return query.offset(skip).limit(limit).all()

@router.get("/")
def get_all_questions(
    exam_type_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    command = GetQuestionsCommand(
        exam_type_id=exam_type_id,
        subject_id=subject_id,
        skip=skip,
        limit=limit
    )
    questions = db.query(Question)
    if command.exam_type_id:
        questions = questions.filter(Question.exam_type_id == command.exam_type_id)
    if command.subject_id:
        questions = questions.filter(Question.subject_id == command.subject_id)
    return questions.offset(command.skip).limit(command.limit).all()

# async def get_all_questions(
#     exam_type_id: Optional[int] = Query(None),
#     subject_id: Optional[int] = Query(None),
#     skip: int = Query(0),
#     limit: int = Query(100),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     query = GetQuestionsQuery(
#         exam_type_id=exam_type_id,
#         subject_id=subject_id,
#         skip=skip,
#         limit=limit
#     )

#     return db.query(Question).offset(query.skip).limit(query.limit).all()
    # handler = GetQuestionsHandler(db)
    # return get_all_questions(query)


@router.get("/exam-type/{exam_type_id}/subject/{subject_id}", response_model=List[QuestionResponse])
def get_questions_by_exam_type_and_subject(exam_type_id: int, subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    questions = db.query(Question).filter(Question.exam_type_id == exam_type_id, Question.subject_id == subject_id).all()
    return [QuestionResponse.model_validate(q) for q in questions]

@router.get("/exam-type/{exam_type_id}", response_model=List[QuestionResponse])
def get_questions_by_exam_type(exam_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    questions = db.query(Question).filter(Question.exam_type_id == exam_type_id).all()
    return [QuestionResponse.model_validate(q) for q in questions]

@router.get("/subject/{subject_id}", response_model=List[QuestionResponse])
def get_questions_by_subject(subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    questions = db.query(Question).filter(Question.subject_id == subject_id).all()
    return [QuestionResponse.model_validate(q) for q in questions]

@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return QuestionResponse.model_validate(question)

@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, question_update: QuestionUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    for field, value in question_update.model_dump(exclude_unset=True).items():
        setattr(question, field, value)
    
    db.commit()
    db.refresh(question)
    return QuestionResponse.model_validate(question)

@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}

@router.post("/bulk", response_model=List[QuestionResponse])
def create_bulk_questions(questions: List[QuestionCreate], db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    db_questions = []
    for question_data in questions:
        db_question = Question(**question_data.model_dump())
        db.add(db_question)
        db_questions.append(db_question)
    
    db.commit()
    for q in db_questions:
        db.refresh(q)
    
    return [QuestionResponse.model_validate(q) for q in db_questions]