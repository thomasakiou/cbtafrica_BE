"""
User Routes - API endpoints for user management

This module handles all user-related operations including:
- User registration (public endpoint)
- User authentication/login (public endpoint) 
- User profile management (authenticated endpoints)
- User listing and administration (authenticated endpoints)

Follows Domain-Driven Design (DDD) pattern with:
- Routes handle HTTP requests/responses
- Commands encapsulate business operations
- Handlers contain business logic
- Models represent database entities
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from typing import List

from app.infrastructure.database.connection import get_db
from app.application.handlers.user_handlers import UserHandler
from app.application.commands.user_commands import (
    CreateUserCommand, UpdateUserCommand, 
    DeleteUserCommand, AuthenticateUserCommand,
    BulkUploadUsersCommand
)
from app.domain.users.schemas import (
    UserCreate, UserUpdate, UserResponse, 
    UserLogin, Token, BulkUserResponse
)
from app.infrastructure.auth import get_current_user
from app.infrastructure.database.models import User
from fastapi.security import HTTPAuthorizationCredentials
from app.infrastructure.auth import security
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.config import settings

# FastAPI router for grouping user-related endpoints
router = APIRouter()

# @router.get("/me", response_model=UserResponse)
# def get_current_user_profile(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get the currently authenticated user's profile.
#     This route is used by the frontend to validate login sessions
#     and determine user roles (admin vs student).
#     """
#     return current_user


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account (PUBLIC ENDPOINT)
    
    This is one of the few endpoints that doesn't require authentication.
    Creates a new user account with hashed password and default 'student' role.
    
    Args:
        user: User registration data (username, email, password, full_name)
        db: Database session dependency
    
    Returns:
        UserResponse: Created user data (without password)
        
    Raises:
        HTTPException 400: If username/email already exists or validation fails
    """
    handler = UserHandler(db)
    try:
        command = CreateUserCommand(user_data=user)
        return handler.create_user(command)
    except Exception as e:
        print(f"Registration error: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# @router.post("/login", response_model=Token)
# def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
#     """
#     Authenticate user and return JWT token (PUBLIC ENDPOINT)
    
#     Validates username/password and returns a JWT token for accessing
#     protected endpoints. Token expires after configured time period.
    
#     Args:
#         user_login: Login credentials (username, password)
#         db: Database session dependency
        
#     Returns:
#         Token: JWT access token and token type
        
#     Raises:
#         HTTPException 401: If credentials are invalid
#     """
#     handler = UserHandler(db)
#     try:
#         command = AuthenticateUserCommand(username=user_login.username, password=user_login.password)
#         return handler.authenticate_user(command)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/login", response_model=dict)  # Changed response_model
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token with user data (PUBLIC ENDPOINT)
    
    Validates username/password and returns a JWT token along with user data
    for accessing protected endpoints. Token expires after configured time period.
    
    Args:
        user_login: Login credentials (username, password)
        db: Database session dependency
        
    Returns:
        dict: Contains access token, token type, and user data
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    handler = UserHandler(db)
    try:
        command = AuthenticateUserCommand(username=user_login.username, password=user_login.password)
        return handler.authenticate_user(command)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/", response_model=list[UserResponse])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get list of all users with pagination (AUTHENTICATED ENDPOINT)
    
    Returns paginated list of all users in the system. Useful for
    administration and user management interfaces.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (max 100)
        db: Database session dependency
        current_user: Currently authenticated user (from JWT token)
        
    Returns:
        list[UserResponse]: List of user data (without passwords)
    """
    handler = UserHandler(db)
    return handler.get_all_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get specific user by ID (AUTHENTICATED ENDPOINT)
    
    Retrieves detailed information about a specific user.
    Could be enhanced to restrict access to own profile or admin-only.
    
    Args:
        user_id: ID of the user to retrieve
        db: Database session dependency
        current_user: Currently authenticated user (from JWT token)
        
    Returns:
        UserResponse: User data (without password)
        
    Raises:
        HTTPException 404: If user not found
    """
    handler = UserHandler(db)
    try:
        return handler.get_user_by_id(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update user information (AUTHENTICATED ENDPOINT)
    
    Updates user profile information. Only provided fields are updated.
    Could be enhanced to restrict users to updating only their own profile.
    
    Args:
        user_id: ID of the user to update
        user_update: Fields to update (all optional)
        db: Database session dependency
        current_user: Currently authenticated user (from JWT token)
        
    Returns:
        UserResponse: Updated user data
        
    Raises:
        HTTPException 404: If user not found
    """
    handler = UserHandler(db)
    try:
        command = UpdateUserCommand(user_id=user_id, user_data=user_update)
        return handler.update_user(command)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete user account (AUTHENTICATED ENDPOINT)
    
    Permanently removes a user account from the system.
    Should be restricted to admin users or account owners only.
    Consider soft delete (is_active=False) instead of hard delete.
    
    Args:
        user_id: ID of the user to delete
        db: Database session dependency
        current_user: Currently authenticated user (from JWT token)
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 404: If user not found
    """
    try:
        handler = UserHandler(db)
        command = DeleteUserCommand(user_id=user_id)
        handler.delete_user(command)
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/bulk-upload", response_model=BulkUserResponse, status_code=status.HTTP_201_CREATED)
async def bulk_upload_users(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk upload users from CSV or Excel file (AUTHENTICATED ENDPOINT)
    
    Upload a CSV or Excel file containing user data to create multiple users at once.
    Required fields: username, password, full_name
    Optional fields: email
    
    File format (CSV/Excel):
    username,email,password,full_name
    user1,user1@example.com,password123,User One
    user2,,password456,User Two
    
    Args:
        file: CSV or Excel file containing user data
        db: Database session dependency
        current_user: Currently authenticated user (from JWT token)
        
    Returns:
        BulkUserResponse: Summary of the import operation
        
    Raises:
        HTTPException 400: If file is invalid or empty
        HTTPException 422: If file format is not supported
    """
    if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be a CSV or Excel file"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse file based on extension
        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        else:  # Excel file
            df = pd.read_excel(BytesIO(content))
        
        # Convert to list of dicts
        users_data = df.replace({pd.NA: None}).to_dict('records')
        
        if not users_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty or could not be processed"
            )
        
        # Process the upload
        handler = UserHandler(db)
        command = BulkUploadUsersCommand(
            users=users_data,
            current_user_id=current_user.id
        )
        
        result = handler.bulk_upload_users(command)
        return result
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty or could not be processed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/refresh-token", response_model=dict)
def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Refresh an existing JWT token. Accepts the current token in the
    Authorization header and returns a new access token with extended
    expiration. Implements a short grace period for recently expired tokens.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        # Try to decode and verify expiration normally
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError as e:
        # Handle expired token with a short grace period
        if "expired" in str(e).lower():
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    options={"verify_exp": False}
                )

                exp = payload.get("exp")
                if not exp:
                    raise credentials_exception

                expired_at = datetime.utcfromtimestamp(exp)
                # Allow refresh within 10 minutes after expiry
                if datetime.utcnow() - expired_at > timedelta(minutes=10):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token expired beyond grace period, please login again",
                    )

                username = payload.get("sub")
                if username is None:
                    raise credentials_exception

            except JWTError:
                raise credentials_exception
        else:
            # Malformed or invalid signature
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Verify user still exists and is active
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise credentials_exception

    # Create new token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires
    new_token = jwt.encode({"sub": username, "exp": expire, "iat": datetime.utcnow()}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"access_token": new_token, "token_type": "bearer"}