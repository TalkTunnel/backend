import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.core.database import get_db
from src.schemas.chat import ChatResponse
from src.schemas.message import MessageResponse
from src.services.chat_service import ChatService
from src.api.deps import get_current_user
from src.models.user import User

router = APIRouter(prefix="/chats", tags=["chats"])

@router.get("/", response_model=List[ChatResponse])
async def get_my_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить все чаты пользователя"""
    chat_service = ChatService(db)
    chats = await chat_service.get_user_chats(current_user.id)
    return chats

@router.post("/private/{user_id}", response_model=ChatResponse)
async def create_private_chat(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать личный чат с пользователем"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot create chat with yourself"
        )
    
    chat_service = ChatService(db)
    chat = await chat_service.create_private_chat(current_user.id, user_id)
    return chat

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить информацию о чате"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat_with_messages(chat_id, current_user.id)
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return chat["chat"]

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить историю сообщений чата"""
    chat_service = ChatService(db)
    chat_data = await chat_service.get_chat_with_messages(
        chat_id, 
        current_user.id,
        limit=limit,
        offset=offset
    )
    
    if not chat_data:
        raise HTTPException(status_code=404, detail="Chat not found")

    response_messages = []
    for message in chat_data["messages"]:
        encrypted_content = message.encrypted_content
        if isinstance(encrypted_content, str):
            try:
                encrypted_content = json.loads(encrypted_content)
            except json.JSONDecodeError:
                encrypted_content = {"raw": encrypted_content}

        response_messages.append(
            {
                "id": message.id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "encrypted_content": encrypted_content,
                "message_type": message.message_type,
                "status": message.status,
                "reply_to_id": message.reply_to_id,
                "is_edited": message.is_edited,
                "created_at": message.created_at,
                "updated_at": message.updated_at,
                "sender": None,
                "attachments": [],
                "reactions": [],
            }
        )

    return response_messages