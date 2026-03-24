from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    VerifyEmailRequest,
    ResendOtpRequest,
    RegisterOtpResponse,
)
from src.services.user_service import UserService
from src.core.security import create_access_token, create_refresh_token
from src.api.deps import get_current_user
from src.models.user import User
from src.core.redis_client import get_redis
from src.services.otp_service import OtpService
from src.services.email_service import EmailService
from src.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=RegisterOtpResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя и отправка OTP на email"""
    user_service = UserService(db)
    
    try:
        user = await user_service.create_user(user_data)
        redis = await get_redis()
        otp_service = OtpService(redis)
        otp_code = otp_service.generate_otp()
        await otp_service.store_otp(user.email, otp_code)

        # Отправка в фоне, чтобы не блокировать ответ API.
        background_tasks.add_task(EmailService().send_otp_email, user.email, otp_code)

        return {
            "message": "OTP sent to your email",
            "email": user.email,
            "expires_in": settings.OTP_TTL_SECONDS,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/verify-email", response_model=Token)
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """Проверка OTP кода и подтверждение email"""
    user_service = UserService(db)
    user = await user_service.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    redis = await get_redis()
    otp_service = OtpService(redis)
    is_valid, message = await otp_service.verify_otp(payload.email, payload.otp)
    if not is_valid:
        if message == "Too many attempts":
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    if not user.is_verified:
        user = await user_service.mark_user_verified(user)

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/resend-otp")
async def resend_otp(
    payload: ResendOtpRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Повторная отправка OTP кода на email"""
    user_service = UserService(db)
    user = await user_service.get_user_by_email(payload.email)
    if not user:
        return {"message": "If this email exists, OTP has been sent"}

    redis = await get_redis()
    otp_service = OtpService(redis)
    if await otp_service.has_resend_cooldown(payload.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait before requesting a new OTP",
        )

    otp_code = otp_service.generate_otp()
    await otp_service.store_otp(payload.email, otp_code)
    background_tasks.add_task(EmailService().send_otp_email, payload.email, otp_code)

    return {
        "message": "OTP sent to your email",
        "expires_in": settings.OTP_TTL_SECONDS,
    }


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Логин пользователя"""
    user_service = UserService(db)
    
    # Определяем, что использовать для входа
    identifier = login_data.username or login_data.email
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email required"
        )
    
    user = await user_service.authenticate_user(identifier, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not verified",
        )
    
    # Создаем токены
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # TODO: Сохранить refresh токен в базе данных
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Выход из системы"""
    # TODO: Инвалидировать refresh токен
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user