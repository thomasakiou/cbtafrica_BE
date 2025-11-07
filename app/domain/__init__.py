# Import all schemas to ensure proper model resolution
from app.domain.tests.schemas import TestWithQuestions
from app.domain.questions.schemas import QuestionResponse

# Rebuild models to resolve forward references
TestWithQuestions.model_rebuild()