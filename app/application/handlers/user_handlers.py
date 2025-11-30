from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from app.infrastructure.database.models import User
from app.application.commands.user_commands import (
    CreateUserCommand, UpdateUserCommand, 
    DeleteUserCommand, AuthenticateUserCommand,
    BulkUploadUsersCommand
)
from app.domain.users.schemas import UserResponse, Token, BulkUserResponse, BulkUserItem

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

class UserHandler:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, command: CreateUserCommand) -> UserResponse:
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.username == command.user_data.username) | 
            (User.email == command.user_data.email)
        ).first()
        if existing_user:
            raise ValueError("User with this username or email already exists")
        
        try:
            # Truncate password to 72 bytes for bcrypt compatibility
            password = command.user_data.password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
            hashed_password = pwd_context.hash(password)
            db_user = User(
                username=command.user_data.username,
                email=command.user_data.email,
                hashed_password=hashed_password,
                full_name=command.user_data.full_name,
                role=command.user_data.role
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return UserResponse.model_validate(db_user)
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create user: {str(e)}")
    
    # def authenticate_user(self, command: AuthenticateUserCommand) -> Token:
    #     user = self.db.query(User).filter(User.username == command.username).first()
    #     if not user or not pwd_context.verify(command.password, user.hashed_password):
    #         raise ValueError("Invalid credentials")
        
    #     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #     access_token = self._create_access_token(
    #         data={"sub": user.username}, expires_delta=access_token_expires
    #     )
    #     return Token(access_token=access_token, token_type="bearer")

    def authenticate_user(self, command: AuthenticateUserCommand) -> dict:  # Changed return type to dict
        user = self.db.query(User).filter(User.username == command.username).first()
        if not user or not pwd_context.verify(command.password, user.hashed_password):
            raise ValueError("Invalid credentials")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self._create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Return both the token and user data
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role
            }
        }
    
    def get_user_by_id(self, user_id: int) -> UserResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        return UserResponse.model_validate(user)
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
        users = self.db.query(User).offset(skip).limit(limit).all()
        return [UserResponse.model_validate(user) for user in users]
    
    def update_user(self, command: UpdateUserCommand) -> UserResponse:
        user = self.db.query(User).filter(User.id == command.user_id).first()
        if not user:
            raise ValueError("User not found")
        
        for field, value in command.user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.model_validate(user)
    
    def delete_user(self, command: DeleteUserCommand) -> None:
        db_user = self.db.query(User).filter(User.id == command.user_id).first()
        if not db_user:
            raise ValueError("User not found")
        self.db.delete(db_user)
        self.db.commit()
        
    def bulk_upload_users(self, command: BulkUploadUsersCommand) -> BulkUserResponse:
        """
        Bulk upload users from a file (CSV/Excel)
        
        Args:
            command: BulkUploadUsersCommand containing user data and current user ID
            
        Returns:
            BulkUserResponse with import statistics and details
        """
        from app.domain.users.schemas import UserCreate
        
        response = BulkUserResponse(
            total_processed=0,
            successful=0,
            failed=0,
            details=[]
        )
        
        for user_data in command.users:
            response.total_processed += 1
            try:
                # Validate user data matches expected schema
                user_item = BulkUserItem(**user_data)
                
                # Check for existing user with same username or email
                existing_user = self.db.query(User).filter(
                    (User.username == user_item.username) | 
                    (User.email == user_item.email)
                ).first()
                
                if existing_user:
                    raise ValueError(f"User with username '{user_item.username}' or email '{user_item.email}' already exists")
                
                # Create user
                create_cmd = CreateUserCommand(
                    user_data=UserCreate(
                        username=user_item.username,
                        email=user_item.email or f"{user_item.username}@example.com",
                        password=user_item.password,
                        full_name=user_item.full_name,
                        role="student"  # Default role for bulk uploads
                    )
                )
                
                self.create_user(create_cmd)
                response.successful += 1
                response.details.append({
                    "username": user_item.username,
                    "status": "success",
                    "message": "User created successfully"
                })
                
            except Exception as e:
                response.failed += 1
                response.details.append({
                    "username": user_data.get('username', 'unknown'),
                    "status": "failed",
                    "message": str(e)
                })
                # Continue with next user even if one fails
                self.db.rollback()
                continue
                
            # Commit after each user to maintain consistency
            self.db.commit()
            
        return response
    
    def _create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt