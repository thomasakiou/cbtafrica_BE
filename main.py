from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.presentation.routes import users, tests, questions, attempts, results, exam_types, subjects
from app.infrastructure.database.connection import engine, SessionLocal
from app.infrastructure.database.models import Base
from app.infrastructure.admin_setup import create_admin_user
from app.infrastructure.database.models import ExamType, Subject

app = FastAPI(title="CBT Application Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Create admin user and default data on startup
db = SessionLocal()
try:
    create_admin_user(db)
    
    # Create default exam types if they don't exist
    # exam_types = ["NECO", "WAEC", "JAMB", "NABTEB"]
    # for exam_type_name in exam_types:
    #     existing = db.query(ExamType).filter(ExamType.name == exam_type_name).first()
    #     if not existing:
    #         exam_type = ExamType(name=exam_type_name, description=f"{exam_type_name} examination")
    #         db.add(exam_type)

    default_exam_types = ["NECO", "WAEC", "JAMB", "NABTEB"]
    for exam_type_name in default_exam_types:
        existing = db.query(ExamType).filter(ExamType.name == exam_type_name).first()
        if not existing:
            exam_type = ExamType(name=exam_type_name, description=f"{exam_type_name} examination")
            db.add(exam_type)
    
    # Create default subjects if they don't exist
    # subjects = ["Mathematics", "English", "Physics", "Chemistry", "Biology", "Economics", "Government", "Literature"]
    # for subject_name in subjects:
    #     existing = db.query(Subject).filter(Subject.name == subject_name).first()
    #     if not existing:
    #         subject = Subject(name=subject_name, description=f"{subject_name} subject")
    #         db.add(subject)
    
    db.commit()
finally:
    db.close()

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tests.router, prefix="/api/v1/tests", tags=["tests"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(attempts.router, prefix="/api/v1/attempts", tags=["attempts"])
app.include_router(results.router, prefix="/api/v1/results", tags=["results"])
app.include_router(exam_types.router, prefix="/api/v1/exam-types", tags=["exam-types"])
app.include_router(subjects.router, prefix="/api/v1/subjects", tags=["subjects"])

@app.get("/")
def read_root():
    return {"message": "CBT Application Backend API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)