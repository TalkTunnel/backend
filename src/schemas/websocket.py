from pydantic import BaseModel
from typing import Optional, Any, Dict
from enum import Enum

class WebSocketEventType(str, Enum):
    # Клиент -> Сервер
    AUTH = "auth"
    SEND_MESSAGE = "send_message"
    TYPING = "typing"
    READ_RECEIPT = "read_receipt"
    DELETE_MESSAGE = "delete_message"
    JOIN_CHAT = "join_chat"
    LEAVE_CHAT = "leave_chat"
    
    # Сервер -> Клиент
    NEW_MESSAGE = "new_message"
    MESSAGE_DELIVERED = "message_delivered"
    MESSAGE_READ = "message_read"
    USER_TYPING = "user_typing"
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
    CHAT_JOINED = "chat_joined"
    CHAT_LEFT = "chat_left"
    ERROR = "error"

class WebSocketMessage(BaseModel):
    event: WebSocketEventType
    data: Dict[str, Any]
    request_id: Optional[str] = None

class AuthPayload(BaseModel):
    token: str

class SendMessagePayload(BaseModel):
    chat_id: int
    encrypted_content: Dict[str, str]  # ciphertext, nonce, tag
    encrypted_key: Optional[str] = None
    reply_to_id: Optional[int] = None
    message_type: str = "text"

class TypingPayload(BaseModel):
    chat_id: int
    is_typing: bool

class ReadReceiptPayload(BaseModel):
    message_id: int
    chat_id: int

class JoinChatPayload(BaseModel):
    chat_id: int