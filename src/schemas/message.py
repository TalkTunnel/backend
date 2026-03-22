from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any
from src.schemas.user import UserPublic

class EncryptedContent(BaseModel):
    """Структура зашифрованного сообщения"""
    ciphertext: str
    nonce: str
    tag: str
    ephemeral_key: Optional[str] = None  # Для ECDH

class MessageBase(BaseModel):
    message_type: str = Field("text", pattern="^(text|image|file|voice|video)$")
    reply_to_id: Optional[int] = None

class MessageCreate(MessageBase):
    """Создание сообщения (клиент присылает зашифрованный контент)"""
    encrypted_content: EncryptedContent
    encrypted_key: Optional[str] = None  # Для групповых чатов

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    encrypted_content: dict  # Зашифрованный контент (только для владельца)
    message_type: str
    status: str
    reply_to_id: Optional[int]
    is_edited: bool
    created_at: datetime
    updated_at: datetime
    
    sender: Optional[UserPublic]
    attachments: List["AttachmentResponse"] = []
    reactions: List["ReactionResponse"] = []
    
    class Config:
        from_attributes = True

class MessageDeliveryResponse(BaseModel):
    user_id: int
    status: str
    delivered_at: datetime
    read_at: Optional[datetime]
    user: UserPublic
    
    class Config:
        from_attributes = True

class MessageUpdate(BaseModel):
    """Обновление сообщения (edit)"""
    encrypted_content: EncryptedContent

class AttachmentResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size: int
    storage_path: str
    thumbnail_path: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReactionResponse(BaseModel):
    id: int
    message_id: int
    user_id: int
    emoji: str
    created_at: datetime
    user: UserPublic
    
    class Config:
        from_attributes = True

class ReactionCreate(BaseModel):
    emoji: str = Field(..., max_length=20)

# Для циклических импортов
MessageResponse.model_rebuild()