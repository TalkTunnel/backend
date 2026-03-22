from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import intersect, select, and_
from typing import List, Optional
from src.models.chat import Chat, ChatParticipant
from src.models.user import User
from src.models.message import Message


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_private_chat(self, user1_id: int, user2_id: int) -> Chat:
        """Создание личного чата"""
        # Уже есть приватный чат, где состоят оба пользователя (пересечение chat_id)
        shared_chat_ids = intersect(
            select(ChatParticipant.chat_id).where(ChatParticipant.user_id == user1_id),
            select(ChatParticipant.chat_id).where(ChatParticipant.user_id == user2_id),
        )
        existing = await self.db.execute(
            select(Chat)
            .where(Chat.type == "private", Chat.id.in_(shared_chat_ids))
            .limit(1)
        )
        existing_chat = existing.scalar_one_or_none()
        if existing_chat:
            return existing_chat
        
        # Создаем новый чат
        chat = Chat(
            type="private",
            is_encrypted=True
        )
        self.db.add(chat)
        await self.db.flush()
        
        # Добавляем участников
        participants = [
            ChatParticipant(chat_id=chat.id, user_id=user1_id, role="owner"),
            ChatParticipant(chat_id=chat.id, user_id=user2_id, role="member")
        ]
        self.db.add_all(participants)
        
        await self.db.commit()
        await self.db.refresh(chat)
        
        return chat
    
    async def get_user_chats(self, user_id: int) -> List[Chat]:
        """Получение всех чатов пользователя"""
        result = await self.db.execute(
            select(Chat)
            .join(ChatParticipant)
            .where(ChatParticipant.user_id == user_id)
            .order_by(Chat.updated_at.desc())
        )
        return result.scalars().all()
    
    async def get_chat_with_messages(
        self, 
        chat_id: int, 
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> Optional[dict]:
        """Получение чата с сообщениями"""
        # Проверяем доступ к чату
        participant = await self.db.execute(
            select(ChatParticipant)
            .where(
                and_(
                    ChatParticipant.chat_id == chat_id,
                    ChatParticipant.user_id == user_id
                )
            )
        )
        if not participant.scalar_one_or_none():
            return None
        
        # Получаем чат
        chat_result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        chat = chat_result.scalar_one_or_none()
        
        if not chat:
            return None
        
        # Получаем сообщения
        messages_result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        messages = messages_result.scalars().all()
        
        return {
            "chat": chat,
            "messages": messages[::-1]  # Переворачиваем для хронологического порядка
        }

    async def check_participant(self, chat_id: int, user_id: int) -> bool:
        """Проверка, является ли пользователь участником чата"""
        result = await self.db.execute(
            select(ChatParticipant)
            .where(
                ChatParticipant.chat_id == chat_id,
                ChatParticipant.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_chat_participants(self, chat_id: int) -> List[ChatParticipant]:
        """Получение всех участников чата"""
        result = await self.db.execute(
            select(ChatParticipant)
            .where(ChatParticipant.chat_id == chat_id)
        )
        return result.scalars().all()

    async def get_chat_participant_ids(self, chat_id: int) -> List[int]:
        """Получение ID всех участников чата"""
        result = await self.db.execute(
            select(ChatParticipant.user_id)
            .where(ChatParticipant.chat_id == chat_id)
        )
        return result.scalars().all()