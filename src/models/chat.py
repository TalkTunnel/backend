from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    chat_id = Column(Integer, ForeignKey("chats.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(20), nullable=False, default="member")
    joined_at = Column(DateTime, default=func.now())
    last_read_message_id = Column(Integer, nullable=True)

    chat = relationship(
        "Chat",
        back_populates="participant_links",
        overlaps="chats,participants,chat_memberships",
    )
    user = relationship(
        "User",
        back_populates="chat_memberships",
        overlaps="chats,participants,participant_links",
    )


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # 'private' или 'group'
    name = Column(String(100), nullable=True)  # для групповых чатов
    is_encrypted = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    participant_links = relationship(
        "ChatParticipant", back_populates="chat", cascade="all, delete-orphan"
    )
    participants = relationship(
        "User",
        secondary="chat_participants",
        back_populates="chats",
        overlaps="participant_links,chat_memberships,chat,user",
    )