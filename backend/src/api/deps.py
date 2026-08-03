from collections.abc import AsyncGenerator, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import async_session_maker
from src.core.security import decode_token
from src.db.auth import TokenPayload
from src.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_service[T](service_cls: type[T]) -> Callable[[SessionDep], T]:
    def _factory(session: SessionDep) -> T:
        return service_cls(session)

    return _factory


def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
        token_payload = TokenPayload(sub=sub)

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    return token_payload.sub


AuthServiceDep = Annotated[AuthService, Depends(get_service(AuthService))]
UserIdDep = Annotated[str, Depends(get_current_user_id)]
