from pydantic import BaseModel
from app.domain.users.schemas import UserCreate, UserUpdate

class CreateUserCommand(BaseModel):
    user_data: UserCreate

class UpdateUserCommand(BaseModel):
    user_id: int
    user_data: UserUpdate

class DeleteUserCommand(BaseModel):
    user_id: int

class AuthenticateUserCommand(BaseModel):
    username: str
    password: str


class BulkUploadUsersCommand(BaseModel):
    """Command for bulk uploading users from a file"""
    users: list[dict]
    current_user_id: int  # ID of the user performing the import