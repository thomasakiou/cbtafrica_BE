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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.handlers.user_handlers import UserHandler
from app.application.commands.user_commands import CreateUserCommand, UpdateUserCommand, DeleteUserCommand, AuthenticateUserCommand
from app.domain.users.schemas import UserCreate, UserUpdate, UserResponse, UserLogin, Token
from app.infrastructure.auth import get_current_user
from app.infrastructure.database.models import User

# FastAPI router for grouping user-related endpoints
router = APIRouter()

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

@router.post("/login", response_model=Token)
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token (PUBLIC ENDPOINT)
    
    Validates username/password and returns a JWT token for accessing
    protected endpoints. Token expires after configured time period.
    
    Args:
        user_login: Login credentials (username, password)
        db: Database session dependency
        
    Returns:
        Token: JWT access token and token type
        
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
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
    handler = UserHandler(db)
    try:
        command = DeleteUserCommand(user_id=user_id)
        handler.delete_user(command)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")