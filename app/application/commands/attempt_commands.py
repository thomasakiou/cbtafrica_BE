from pydantic import BaseModel
from app.domain.attempts.schemas import AttemptCreate, AttemptSubmit

class StartAttemptCommand(BaseModel):
    user_id: int
    attempt_data: AttemptCreate

class SubmitAttemptCommand(BaseModel):
    submission: AttemptSubmit

class GetUserAttemptsCommand(BaseModel):
    user_id: int

class GetAttemptCommand(BaseModel):
    attempt_id: int