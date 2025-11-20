from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Base class for all database models using SQLAlchemy's declarative base
Base = declarative_base()

class User(Base):
    """
    User Model - Represents system users (students, teachers, admins)
    
    This model stores user account information and authentication data.
    Users can have different roles (student, teacher, admin) which determine
    their permissions in the system. Students take tests, teachers/admins
    can create and manage tests.
    """
    __tablename__ = "users"
    
    # Primary key - unique identifier for each user
    id = Column(Integer, primary_key=True, index=True)
    
    # Unique username for login - indexed for fast lookups
    username = Column(String, unique=True, index=True)
    
    # Unique email address - indexed for fast lookups
    email = Column(String, unique=True, index=True)
    
    # Bcrypt hashed password - never store plain text passwords
    hashed_password = Column(String)
    
    # User's display name
    full_name = Column(String)
    
    # User role: 'student', 'teacher', 'admin' - determines permissions
    role = Column(String, default="student")
    
    # Account status - allows disabling users without deletion
    is_active = Column(Boolean, default=True)
    
    # Account creation timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: One user can have many test attempts
    attempts = relationship("Attempt", back_populates="user")

class ExamType(Base):
    """
    ExamType Model - Represents different examination bodies/types
    
    Stores different types of examinations like NECO, WAEC, JAMB, NABTEB.
    Each exam type has its own standards, question formats, and requirements.
    Only admin users can create and manage exam types.
    """
    __tablename__ = "exam_types"
    
    # Primary key - unique identifier for each exam type
    id = Column(Integer, primary_key=True, index=True)
    
    # Exam type name (e.g., "NECO", "WAEC", "JAMB", "NABTEB") - unique and indexed
    name = Column(String, unique=True, index=True)
    
    # Optional description explaining the exam type
    description = Column(Text)
    
    # Exam type creation timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships: One exam type can have many tests and questions
    tests = relationship("Test", back_populates="exam_type")
    questions = relationship("Question", back_populates="exam_type")

class Subject(Base):
    """
    Subject Model - Represents academic subjects
    
    Stores different academic subjects like Mathematics, English, Physics, etc.
    Subjects are used to categorize questions and tests by academic discipline.
    Only admin users can create and manage subjects.
    """
    __tablename__ = "subjects"
    
    # Primary key - unique identifier for each subject
    id = Column(Integer, primary_key=True, index=True)
    
    # Subject name (e.g., "Mathematics", "English", "Physics") - unique and indexed
    name = Column(String, unique=True, index=True)
    
    # Optional description explaining what the subject covers
    description = Column(Text)
    
    # Subject creation timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships: One subject can have many tests and questions
    tests = relationship("Test", back_populates="subject")
    questions = relationship("Question", back_populates="subject")

# Association table for many-to-many relationship between tests and questions
test_questions = Table('test_questions', Base.metadata,
    Column('test_id', Integer, ForeignKey('tests.id'), primary_key=True),
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True)
)

class Test(Base):
    """
    Test Model - Represents a dynamically generated test/exam
    
    Tests are now dynamically created based on exam type, subject, duration,
    and number of questions. Questions are randomly selected from the question
    pool matching the specified exam type and subject criteria.
    """
    __tablename__ = "tests"
    
    # Primary key - unique identifier for each test
    id = Column(Integer, primary_key=True, index=True)
    
    # Auto-generated test title based on exam type and subject
    title = Column(String, index=True)
    
    # Foreign key linking to exam type (NECO, WAEC, JAMB, NABTEB)
    exam_type_id = Column(Integer, ForeignKey("exam_types.id"))
    
    # Foreign key linking to subject (Mathematics, English, etc.)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    # Time limit for the test in minutes (set by user during test creation)
    duration_minutes = Column(Integer)
    
    # Number of questions in this test (set by user during test creation)
    question_count = Column(Integer)
    
    # Maximum possible score (calculated as question_count * marks_per_question)
    total_marks = Column(Integer)
    
    # Minimum score required to pass (typically 50% of total_marks)
    passing_marks = Column(Integer)
    
    # Whether the test is currently available to students
    is_active = Column(Boolean, default=True)
    
    # Foreign key - which user created this test
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Test creation timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exam_type = relationship("ExamType", back_populates="tests")
    subject = relationship("Subject", back_populates="tests")
    questions = relationship("Question", secondary="test_questions", back_populates="tests")
    attempts = relationship("Attempt", back_populates="test")

class Question(Base):
    """
    Question Model - Individual questions in the question bank
    
    Questions are stored in a central question bank and belong to specific
    exam types and subjects. When a test is created, questions are randomly
    selected from this bank based on the specified exam type and subject.
    Only admin users can create and manage questions.
    """
    __tablename__ = "questions"
    
    # Primary key - unique identifier for each question
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key - which exam type this question belongs to (NECO, WAEC, etc.)
    exam_type_id = Column(Integer, ForeignKey("exam_types.id"))
    
    # Foreign key - which subject this question belongs to (Mathematics, English, etc.)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    # The actual question text/content
    question_text = Column(Text)
    
    # Optional question image URL/path (for questions presented as images)
    question_image = Column(String, nullable=True)
    
    # Type of question: 'multiple_choice', 'true_false', 'essay'
    question_type = Column(String)
    
    # JSON field storing answer options for multiple choice questions
    # Example: {"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"}
    options = Column(JSON)
    
    # The correct answer (letter for MC, "true"/"false" for T/F, text for essay)
    correct_answer = Column(String)
    
    # Optional explanation for the correct answer
    explanation = Column(Text, default=" ")
    
    # Optional explanation image URL/path (for visual explanations)
    explanation_image = Column(String, nullable=True)
    
    # Question creation timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exam_type = relationship("ExamType", back_populates="questions")
    subject = relationship("Subject", back_populates="questions")
    tests = relationship("Test", secondary="test_questions", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

class Attempt(Base):
    """
    Attempt Model - Represents a user's attempt at taking a test
    
    An attempt is created when a user starts a test and tracks the
    entire test-taking session. It records start/end times, current
    status, and final results. This allows for features like resuming
    interrupted tests and detailed analytics.
    """
    __tablename__ = "attempts"
    
    # Primary key - unique identifier for each attempt
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key - which user is taking the test
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Foreign key - which test is being attempted
    test_id = Column(Integer, ForeignKey("tests.id"))
    
    # When the user started the test
    start_time = Column(DateTime, default=datetime.utcnow)
    
    # When the user finished/submitted the test (null if still in progress)
    end_time = Column(DateTime)
    
    # Current status: 'in_progress', 'completed', 'abandoned'
    status = Column(String, default="in_progress")
    
    # Final score achieved (sum of marks from correct answers)
    score = Column(Float)
    
    # Percentage score (score/total_marks * 100)
    percentage = Column(Float)
    
    # Whether the user passed (percentage >= passing percentage)
    passed = Column(Boolean)
    
    # Relationships
    user = relationship("User", back_populates="attempts")
    test = relationship("Test", back_populates="attempts")
    answers = relationship("Answer", back_populates="attempt")

class Answer(Base):
    """
    Answer Model - Individual answers given by users during test attempts
    
    Each answer represents a user's response to a specific question
    during a test attempt. It stores the user's answer, whether it's
    correct, points earned, and time spent. This granular data enables
    detailed analytics and feedback.
    """
    __tablename__ = "answers"
    
    # Primary key - unique identifier for each answer
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key - which attempt this answer belongs to
    attempt_id = Column(Integer, ForeignKey("attempts.id"))
    
    # Foreign key - which question this answers
    question_id = Column(Integer, ForeignKey("questions.id"))
    
    # The user's actual answer (letter, "true"/"false", or essay text)
    answer_text = Column(Text)
    
    # Whether the answer is correct (auto-graded for MC/TF, manual for essays)
    is_correct = Column(Boolean)
    
    # Points awarded for this answer (may be partial credit)
    marks_obtained = Column(Float)
    
    # Time spent on this question in seconds (for analytics)
    time_spent = Column(Integer)
    
    # Relationships
    attempt = relationship("Attempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")

class News(Base):
    """
    News Model - Stores news feed items for display on frontend
    
    This model stores news items that will be displayed in the frontend
    news feed. Each news item includes a title, description, URL to the
    full article, and publication date. This allows the application to
    display curated news content relevant to students and educators.
    """
    __tablename__ = "news"
    
    # Primary key - unique identifier for each news item
    id = Column(Integer, primary_key=True, index=True)
    
    # The news heading/title
    title = Column(String(500), nullable=False)
    
    # Short description of the news
    content = Column(Text, nullable=False)
    
    # URL to the actual news page on the internet
    url = Column(String, nullable=False)
    
    # Date the news was published
    date = Column(DateTime, nullable=False)
    
    # News item creation timestamp (when added to system)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # News item last update timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)