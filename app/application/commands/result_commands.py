from pydantic import BaseModel

class GetAttemptResultCommand(BaseModel):
    attempt_id: int

class GetUserResultsCommand(BaseModel):
    user_id: int

class GetTestAnalyticsCommand(BaseModel):
    test_id: int