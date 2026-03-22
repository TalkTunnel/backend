from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from src.schemas.user import UserPublic

class ChatBase(BaseModel):
    type: str = Field(..., pattern="^(private|group|channel)$")
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    is_encrypted: bool = True
    is_private: bool = False

class ChatCreate(ChatBase):
    participant_ids: List[int] = Field(..., min_length=1)  # ID участников
    group_key_encrypted: Optional[str] = None  # Для групповых чатов

class ChatResponse(ChatBase):
    id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    participants: List[UserPublic]
    unread_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class ChatParticipantResponse(BaseModel):
    chat_id: int
    user_id: int
    role: str
    joined_at: datetime
    last_read_message_id: Optional[int]
    user: UserPublic
    
    class Config:
        from_attributes = True

class UpdateParticipantRole(BaseModel):
    user_id: int
    role: str = Field(..., pattern="^(owner|admin|member)$")