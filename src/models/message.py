from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Зашифрованное содержимое
    encrypted_content = Column(Text, nullable=False)  # JSON: {ciphertext, nonce, tag}
    encrypted_key = Column(Text, nullable=True)  # Для групповых чатов
    
    message_type = Column(String(20), default="text")  # text, image, file, voice, video
    status = Column(String(20), default="sent")  # sent, delivered, read, deleted
    
    reply_to_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    is_edited = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages",
    )
    reply_to = relationship("Message", remote_side=[id], backref="replies")
    deliveries = relationship("MessageDelivery", back_populates="message", cascade="all, delete-orphan")

class MessageDelivery(Base):
    __tablename__ = "message_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(String(20), default="delivered")  # delivered, read
    delivered_at = Column(DateTime, default=func.now())
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    message = relationship("Message", back_populates="deliveries")
    user = relationship("User")