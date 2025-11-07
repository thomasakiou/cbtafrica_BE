from sqlalchemy.orm import Session
from app.infrastructure.database.models import Subject
from app.application.commands.subject_commands import CreateSubjectCommand, UpdateSubjectCommand, DeleteSubjectCommand
from app.domain.subjects.schemas import SubjectResponse

class SubjectHandler:
    def __init__(self, db: Session):
        self.db = db
    
    def create_subject(self, command: CreateSubjectCommand) -> SubjectResponse:
        db_subject = Subject(**command.subject_data.model_dump())
        self.db.add(db_subject)
        self.db.commit()
        self.db.refresh(db_subject)
        return SubjectResponse.model_validate(db_subject)
    
    def get_all_subjects(self, skip: int = 0, limit: int = 100):
        subjects = self.db.query(Subject).offset(skip).limit(limit).all()
        return [SubjectResponse.model_validate(s) for s in subjects]
    
    def get_subject_by_id(self, subject_id: int) -> SubjectResponse:
        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise ValueError("Subject not found")
        return SubjectResponse.model_validate(subject)
    
    def update_subject(self, command: UpdateSubjectCommand) -> SubjectResponse:
        subject = self.db.query(Subject).filter(Subject.id == command.subject_id).first()
        if not subject:
            raise ValueError("Subject not found")
        
        for field, value in command.subject_data.model_dump(exclude_unset=True).items():
            setattr(subject, field, value)
        
        self.db.commit()
        self.db.refresh(subject)
        return SubjectResponse.model_validate(subject)
    
    def delete_subject(self, command: DeleteSubjectCommand) -> bool:
        subject = self.db.query(Subject).filter(Subject.id == command.subject_id).first()
        if not subject:
            raise ValueError("Subject not found")
        
        self.db.delete(subject)
        self.db.commit()
        return True