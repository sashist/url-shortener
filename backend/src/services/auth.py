from fastapi import HTTPException
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.models.users import User, UserCreate
from src.repositories.users import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(self.session)

    async def register_user(self, data: UserCreate) -> User:
        existing_user = await self.repo.get_filtered(email=data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = hash_password(data.password)
        db_user = User(
            email=data.email, full_name=data.full_name, hashed_password=hashed_password
        )
        user: User = await self.repo.add(db_user)
        await self.session.commit()
        logger.bind(user_id=str(user.id), email=user.email).info(
            "User registered successfully"
        )

        return user

    async def login_user(self, data: UserCreate) -> tuple[str, str]:
        user = await self.repo.get_user_with_hash_password(email=data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            logger.bind(email=data.email).warning(
                "Failed login attempt: invalid credentials"
            )

            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        logger.bind(user_id=str(user.id)).info("User logged in")

        return access_token, refresh_token

    async def get_user_by_id(self, user_id: str) -> User:
        user = await self.repo.get_one(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def refresh_tokens(self, refresh_token: str) -> tuple[str, str]:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token missing")

        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")
        except ValueError:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )

        user = await self.repo.get_one(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        logger.bind(user_id=str(user_id)).info("Tokens refreshed")

        return new_access_token, new_refresh_token
