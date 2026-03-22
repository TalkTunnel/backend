from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

# Таблица участников чатов (many-to-many)
chat_participants = Table(
    "chat_participants",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chats.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("joined_at", DateTime, default=func.now()),
    Column("last_read_message_id", Integer, nullable=True)
)

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # 'private' или 'group'
    name = Column(String(100), nullable=True)  # для групповых чатов
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    participants = relationship("User", secondary=chat_participants, backref="chats")