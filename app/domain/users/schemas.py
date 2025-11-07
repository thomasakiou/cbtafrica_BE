from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str = "student"

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password too long (max 72 bytes)')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True


class BulkUserItem(BaseModel):
    """Schema for individual user data in bulk upload"""
    username: str
    email: Optional[EmailStr] = None
    password: str
    full_name: str
    
    # Convert fields to string if they're numbers
    @field_validator('username', 'password', mode='before')
    @classmethod
    def convert_to_string(cls, v, info):
        if v is not None:
            return str(v)
        return v


class BulkUserResponse(BaseModel):
    """Response schema for bulk user upload"""
    total_processed: int
    successful: int
    failed: int
    details: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of operation results with details about each user import attempt"
    )