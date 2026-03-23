from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.user import UserPublic


class ChatBase(BaseModel):
    type: str = Field(..., pattern="^(private|group|channel)$")
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    is_encrypted: bool = True
    is_private: bool = False


class ChatCreate(ChatBase):
    participant_ids: List[int] = Field(..., min_length=1)
    group_key_encrypted: Optional[str] = None


class ChatResponse(BaseModel):
    """Соответствует ORM-модели Chat (без ленивых relationship в async)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    name: Optional[str] = None
    is_encrypted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    participant_ids: List[int] = Field(default_factory=list)
    participant_usernames: List[str] = Field(default_factory=list)

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