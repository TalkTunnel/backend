import secrets

from redis.asyncio import Redis

from src.core.config import settings


class OtpService:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def generate_otp() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def _otp_key(email: str) -> str:
        return f"otp:verify_email:{email.lower()}"

    @staticmethod
    def _attempts_key(email: str) -> str:
        return f"otp:attempts:{email.lower()}"

    @staticmethod
    def _cooldown_key(email: str) -> str:
        return f"otp:cooldown:{email.lower()}"

    async def has_resend_cooldown(self, email: str) -> bool:
        return await self.redis.exists(self._cooldown_key(email)) == 1

    async def store_otp(self, email: str, otp_code: str) -> None:
        ttl = settings.OTP_TTL_SECONDS
        await self.redis.set(self._otp_key(email), otp_code, ex=ttl)
        await self.redis.delete(self._attempts_key(email))
        await self.redis.set(self._cooldown_key(email), "1", ex=settings.OTP_RESEND_COOLDOWN_SECONDS)

    async def verify_otp(self, email: str, otp_code: str) -> tuple[bool, str]:
        key = self._otp_key(email)
        stored_otp = await self.redis.get(key)
        if not stored_otp:
            return False, "OTP expired or not found"

        attempts_key = self._attempts_key(email)
        attempts_raw = await self.redis.get(attempts_key)
        attempts = int(attempts_raw) if attempts_raw else 0
        if attempts >= settings.OTP_MAX_ATTEMPTS:
            return False, "Too many attempts"

        if stored_otp != otp_code:
            attempts += 1
            await self.redis.set(attempts_key, str(attempts), ex=settings.OTP_TTL_SECONDS)
            return False, "Invalid OTP code"

        await self.redis.delete(key)
        await self.redis.delete(attempts_key)
        await self.redis.delete(self._cooldown_key(email))
        return True, "OTP verified"
