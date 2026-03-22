from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import bcrypt
from jose import JWTError, jwt

from src.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля (совместимо с хешами passlib/bcrypt)."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """Хеширование пароля (bcrypt, лимит 72 байта на пароль)."""
    pw = password.encode("utf-8")
    if len(pw) > 72:
        pw = pw[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Создание access токена"""
    to_encode = data.copy()
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Создание refresh токена"""
    to_encode = data.copy()
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Декодирование токена"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """Получение payload из токена"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        return payload
    except JWTError:
        return None