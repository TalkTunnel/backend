from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Управление WebSocket соединениями"""
    
    def __init__(self):
        # Активные соединения: {user_id: {websocket}}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Сопоставление websocket с user_id
        self.connection_to_user: Dict[WebSocket, int] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Подключение пользователя"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_to_user[websocket] = user_id
        
        logger.info(f"User {user_id} connected. Total connections: {len(self.connection_to_user)}")
    
    def disconnect(self, websocket: WebSocket):
        """Отключение пользователя"""
        user_id = self.connection_to_user.pop(websocket, None)
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"User {user_id} disconnected. Total connections: {len(self.connection_to_user)}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Отправить сообщение конкретному пользователю"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast_to_chat(self, message: dict, chat_id: int, exclude_user_id: Optional[int] = None):
        """Отправить сообщение всем участникам чата"""
        # Эта логика будет позже, когда добавим получение участников чата
        # Пока оставляем заглушку
        pass
    
    async def send_to_chat_participants(self, message: dict, user_ids: Set[int]):
        """Отправить сообщение списку пользователей"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def is_user_online(self, user_id: int) -> bool:
        """Проверить, онлайн ли пользователь"""
        return user_id in self.active_connections and bool(self.active_connections[user_id])

# Глобальный экземпляр менеджера
manager = ConnectionManager()