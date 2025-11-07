from sqlalchemy.orm import Session
from app.infrastructure.database.models import ExamType
from app.application.commands.exam_type_commands import CreateExamTypeCommand, UpdateExamTypeCommand, DeleteExamTypeCommand
from app.domain.exam_types.schemas import ExamTypeResponse

class ExamTypeHandler:
    def __init__(self, db: Session):
        self.db = db
    
    def create_exam_type(self, command: CreateExamTypeCommand) -> ExamTypeResponse:
        db_exam_type = ExamType(**command.exam_type_data.model_dump())
        self.db.add(db_exam_type)
        self.db.commit()
        self.db.refresh(db_exam_type)
        return ExamTypeResponse.model_validate(db_exam_type)
    
    def get_all_exam_types(self, skip: int = 0, limit: int = 100):
        exam_types = self.db.query(ExamType).offset(skip).limit(limit).all()
        return [ExamTypeResponse.model_validate(et) for et in exam_types]
    
    def get_exam_type_by_id(self, exam_type_id: int) -> ExamTypeResponse:
        exam_type = self.db.query(ExamType).filter(ExamType.id == exam_type_id).first()
        if not exam_type:
            raise ValueError("Exam type not found")
        return ExamTypeResponse.model_validate(exam_type)
    
    def update_exam_type(self, command: UpdateExamTypeCommand) -> ExamTypeResponse:
        exam_type = self.db.query(ExamType).filter(ExamType.id == command.exam_type_id).first()
        if not exam_type:
            raise ValueError("Exam type not found")
        
        for field, value in command.exam_type_data.model_dump(exclude_unset=True).items():
            setattr(exam_type, field, value)
        
        self.db.commit()
        self.db.refresh(exam_type)
        return ExamTypeResponse.model_validate(exam_type)
    
    def delete_exam_type(self, command: DeleteExamTypeCommand) -> bool:
        exam_type = self.db.query(ExamType).filter(ExamType.id == command.exam_type_id).first()
        if not exam_type:
            raise ValueError("Exam type not found")
        
        self.db.delete(exam_type)
        self.db.commit()
        return True