from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import Question, User
from app.domain.questions.schemas import QuestionCreate, QuestionUpdate, QuestionResponse
from app.infrastructure.auth import require_admin, get_current_user
from app.application.commands.question_commands import GetQuestionsCommand
from app.config import settings
import os
import uuid
from pathlib import Path


router = APIRouter()

def get_file_path_from_url(url_path: str) -> str:
    """
    Convert URL path to file system path.
    
    Args:
        url_path: URL path like "/cbt/uploads/explanation_images/filename.png"
        
    Returns:
        str: File system path like "uploads/explanation_images/filename.png"
    """
    # Remove the root_path prefix if present
    if url_path.startswith(settings.ROOT_PATH):
        url_path = url_path[len(settings.ROOT_PATH):]
    
    # Remove leading slash
    if url_path.startswith("/"):
        url_path = url_path[1:]
    
    return url_path

async def save_question_image(file: UploadFile) -> str:
    """
    Save uploaded question image to disk and return the URL path.
    
    Args:
        file: The uploaded image file
        
    Returns:
        str: The URL path to the saved file
        
    Raises:
        HTTPException: If file validation fails
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Read file content and validate size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.QUESTION_IMAGE_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Return URL path (including root_path) for storage in database
    return f"{settings.ROOT_PATH}/uploads/question_images/{unique_filename}"

async def save_explanation_image(file: UploadFile) -> str:
    """
    Save uploaded explanation image to disk and return the file path.
    
    Args:
        file: The uploaded image file
        
    Returns:
        str: The relative path to the saved file
        
    Raises:
        HTTPException: If file validation fails
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Read file content and validate size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Return URL path (including root_path) for storage in database
    # This ensures the path works with the configured root_path ("/cbt")
    return f"{settings.ROOT_PATH}/uploads/explanation_images/{unique_filename}"

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
    
    # Delete associated question image if it exists
    if question.question_image:
        file_path = get_file_path_from_url(question.question_image)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # Log but don't fail if image deletion fails
                print(f"Failed to delete question image: {e}")
    
    # Delete associated explanation image if it exists
    if question.explanation_image:
        file_path = get_file_path_from_url(question.explanation_image)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # Log but don't fail if image deletion fails
                print(f"Failed to delete explanation image: {e}")
    
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}

@router.post("/{question_id}/upload-explanation-image", response_model=QuestionResponse)
async def upload_explanation_image(
    question_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Upload an explanation image for a question.
    
    This endpoint allows admins to upload an optional explanation image
    for questions where text explanation alone cannot properly explain the concept.
    
    Args:
        question_id: The ID of the question to add the explanation image to
        file: The image file to upload (jpg, jpeg, png, gif, webp)
        db: Database session
        admin: Admin user (authentication required)
        
    Returns:
        QuestionResponse: The updated question with the explanation image path
        
    Raises:
        HTTPException 404: If question not found
        HTTPException 400: If file validation fails
    """
    # Check if question exists
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Delete old explanation image if it exists
    if question.explanation_image:
        file_path = get_file_path_from_url(question.explanation_image)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete old explanation image: {e}")
    
    # Save new explanation image
    file_path = await save_explanation_image(file)
    
    # Update question with new image path
    question.explanation_image = file_path
    db.commit()
    db.refresh(question)
    
    return QuestionResponse.model_validate(question)

@router.delete("/{question_id}/explanation-image")
def delete_explanation_image(
    question_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Delete the explanation image for a question.
    
    Args:
        question_id: The ID of the question
        db: Database session
        admin: Admin user (authentication required)
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 404: If question not found or no image exists
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if not question.explanation_image:
        raise HTTPException(status_code=404, detail="No explanation image found for this question")
    
    # Delete image file from disk
    file_path = get_file_path_from_url(question.explanation_image)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete image file: {str(e)}")
    
    # Update database
    question.explanation_image = None
    db.commit()
    
    return {"message": "Explanation image deleted successfully"}

@router.post("/{question_id}/upload-question-image", response_model=QuestionResponse)
async def upload_question_image(
    question_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Upload a question image.
    
    This endpoint allows admins to upload an image representing the question itself.
    Useful for questions that are better presented as images (diagrams, charts, etc.).
    
    Args:
        question_id: The ID of the question to add the image to
        file: The image file to upload (jpg, jpeg, png, gif, webp)
        db: Database session
        admin: Admin user (authentication required)
        
    Returns:
        QuestionResponse: The updated question with the question image path
        
    Raises:
        HTTPException 404: If question not found
        HTTPException 400: If file validation fails
    """
    # Check if question exists
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Delete old question image if it exists
    if question.question_image:
        file_path = get_file_path_from_url(question.question_image)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete old question image: {e}")
    
    # Save new question image
    file_path = await save_question_image(file)
    
    # Update question with new image path
    question.question_image = file_path
    db.commit()
    db.refresh(question)
    
    return QuestionResponse.model_validate(question)

@router.delete("/{question_id}/question-image")
def delete_question_image(
    question_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Delete the question image for a question.
    
    Args:
        question_id: The ID of the question
        db: Database session
        admin: Admin user (authentication required)
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 404: If question not found or no image exists
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if not question.question_image:
        raise HTTPException(status_code=404, detail="No question image found for this question")
    
    # Delete image file from disk
    file_path = get_file_path_from_url(question.question_image)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete image file: {str(e)}")
    
    # Update database
    question.question_image = None
    db.commit()
    
    return {"message": "Question image deleted successfully"}

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