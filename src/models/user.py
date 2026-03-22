from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    
    # E2EE публичный ключ
    public_key = Column(String(500), nullable=True)

    full_name = Column(String(100), nullable=True)
    bio = Column(String(500), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    chat_memberships = relationship(
        "ChatParticipant",
        back_populates="user",
        overlaps="chats,participants,participant_links",
    )
    chats = relationship(
        "Chat",
        secondary="chat_participants",
        back_populates="participants",
        overlaps="participant_links,chat_memberships,chat,user",
    )
    sent_messages = relationship(
        "Message",
        back_populates="sender",
        foreign_keys="Message.sender_id",
    )