from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from src.models.message import Message, MessageDelivery
from src.models.chat import ChatParticipant
import json
from datetime import datetime

class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_message(
        self,
        chat_id: int,
        sender_id: int,
        encrypted_content: dict,
        message_type: str = "text",
        reply_to_id: Optional[int] = None
    ) -> Message:
        """Создание нового сообщения"""
        message = Message(
            chat_id=chat_id,
            sender_id=sender_id,
            encrypted_content=json.dumps(encrypted_content),
            message_type=message_type,
            reply_to_id=reply_to_id,
            status="sent"
        )
        
        self.db.add(message)
        await self.db.flush()
        
        # Создаем записи доставки для всех участников чата
        participants = await self.db.execute(
            select(ChatParticipant.user_id)
            .where(ChatParticipant.chat_id == chat_id)
        )
        
        for participant in participants.scalars():
            if participant != sender_id:
                delivery = MessageDelivery(
                    message_id=message.id,
                    user_id=participant,
                    status="delivered"
                )
                self.db.add(delivery)
        
        await self.db.commit()
        await self.db.refresh(message)
        
        return message
    
    async def get_message(self, message_id: int) -> Optional[Message]:
        """Получение сообщения по ID"""
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()
    
    async def mark_as_read(self, message_id: int, user_id: int):
        """Отметить сообщение как прочитанное"""
        await self.db.execute(
            update(MessageDelivery)
            .where(
                MessageDelivery.message_id == message_id,
                MessageDelivery.user_id == user_id
            )
            .values(
                status="read",
                read_at=datetime.utcnow()
            )
        )
        await self.db.commit()
    
    async def get_chat_messages(
        self,
        chat_id: int,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Получение истории сообщений чата"""
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Хронологический порядок