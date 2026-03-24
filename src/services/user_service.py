from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional, List
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        # Проверка уникальности
        existing = await self.db.execute(
            select(User).where(
                or_(
                    User.username == user_data.username,
                    User.email == user_data.email
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Username or email already exists")
        
        # Создание пользователя
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            public_key=user_data.public_key,
            full_name=user_data.full_name,
            bio=user_data.bio,
            avatar_url=user_data.avatar_url
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = await self.get_user_by_username_or_email(username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def get_user_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Поиск пользователя по username или email"""
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.username == identifier,
                    User.email == identifier
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Поиск пользователя по email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def mark_user_verified(self, user: User) -> User:
        """Подтверждение email пользователя"""
        user.is_verified = True
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Обновление пользователя"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def search_users(self, query: str, limit: int = 20) -> List[User]:
        """Поиск пользователей"""
        result = await self.db.execute(
            select(User)
            .where(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.full_name.ilike(f"%{query}%")
                )
            )
            .limit(limit)
        )
        return result.scalars().all()