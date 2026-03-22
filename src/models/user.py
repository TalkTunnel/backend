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
    
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    chat_memberships = relationship(
        "ChatParticipant", back_populates="user", overlaps="chats,participants"
    )
    chats = relationship(
        "Chat",
        secondary="chat_participants",
        back_populates="participants",
        overlaps="chat_memberships,participant_links",
    )