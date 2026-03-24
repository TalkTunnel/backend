from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    public_key: str  # E2EE публичный ключ
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

class UserResponse(UserBase):
    id: int
    public_key: Optional[str]
    is_active: bool
    is_verified: bool
    last_seen: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfile(UserResponse):
    """Детальная информация о пользователе для профиля"""
    pass

class UserPublic(BaseModel):
    """Публичная информация о пользователе (для списка контактов)"""
    id: int
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    public_key: Optional[str]
    is_online: bool = False
    last_seen: Optional[datetime]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int  # user_id
    exp: datetime
    type: str  # "access" or "refresh"


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=10)


class ResendOtpRequest(BaseModel):
    email: EmailStr


class RegisterOtpResponse(BaseModel):
    message: str
    email: EmailStr
    expires_in: int

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    public_key: Optional[str] = None