from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.websocket_manager import manager
from src.core.security import decode_token
from src.services.message_service import MessageService
from src.services.chat_service import ChatService
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    """WebSocket эндпоинт для real-time сообщений"""
    
    # Аутентификация через токен в query параметре
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return
    
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    sub = payload.get("sub")
    if sub is None or sub == "":
        await websocket.close(code=1008, reason="Invalid token payload")
        return
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        await websocket.close(code=1008, reason="Invalid token payload")
        return

    await manager.connect(websocket, user_id)
    
    # Инициализируем сервисы
    message_service = MessageService(db)
    chat_service = ChatService(db)
    
    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_json()
            event_type = data.get("event")
            
            if event_type == "send_message":
                chat_id = data.get("chat_id")
                encrypted_content = data.get("encrypted_content")
                reply_to_id = data.get("reply_to_id")
                message_type = data.get("message_type", "text")
                if chat_id is None or encrypted_content is None:
                    await websocket.send_json(
                        {"event": "error", "data": {"message": "chat_id and encrypted_content required"}}
                    )
                    continue
                chat_id = int(chat_id)

                participant = await chat_service.check_participant(chat_id, user_id)
                if not participant:
                    await websocket.send_json({
                        "event": "error",
                        "data": {"message": "Not a participant of this chat"}
                    })
                    continue
                
                # Создаем сообщение
                message = await message_service.create_message(
                    chat_id=chat_id,
                    sender_id=user_id,
                    encrypted_content=encrypted_content,
                    message_type=message_type,
                    reply_to_id=int(reply_to_id) if reply_to_id is not None else None,
                )
                
                # Получаем всех участников чата
                participants = await chat_service.get_chat_participants(chat_id)
                
                # Отправляем сообщение всем участникам
                message_data = {
                    "event": "new_message",
                    "data": {
                        "id": message.id,
                        "chat_id": message.chat_id,
                        "sender_id": message.sender_id,
                        "encrypted_content": message.encrypted_content,
                        "message_type": message.message_type,
                        "reply_to_id": message.reply_to_id,
                        "created_at": message.created_at.isoformat()
                    }
                }
                
                # Отправляем всем участникам, кроме отправителя
                for participant in participants:
                    if participant.user_id != user_id:
                        await manager.send_personal_message(message_data, participant.user_id)
                
                # Подтверждение отправителю
                await websocket.send_json({
                    "event": "message_sent",
                    "data": {"message_id": message.id}
                })
            
            elif event_type == "typing":
                chat_id = data.get("chat_id")
                if chat_id is None:
                    continue
                chat_id = int(chat_id)
                is_typing = data.get("is_typing", True)

                participants = await chat_service.get_chat_participants(chat_id)
                
                typing_data = {
                    "event": "user_typing",
                    "data": {
                        "chat_id": chat_id,
                        "user_id": user_id,
                        "is_typing": is_typing
                    }
                }
                
                for participant in participants:
                    if participant.user_id != user_id:
                        await manager.send_personal_message(typing_data, participant.user_id)
            
            elif event_type == "read_receipt":
                message_id = data.get("message_id")
                if message_id is None:
                    continue
                message_id = int(message_id)

                await message_service.mark_as_read(message_id, user_id)
                
                # Уведомляем отправителя
                message = await message_service.get_message(message_id)
                if message:
                    read_data = {
                        "event": "message_read",
                        "data": {
                            "message_id": message_id,
                            "chat_id": chat_id,
                            "user_id": user_id,
                            "read_at": datetime.utcnow().isoformat()
                        }
                    }
                    await manager.send_personal_message(read_data, message.sender_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"User {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket)