import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlmodel.ext.asyncio.session import AsyncSession

from src.services.links import LinkService
from src.core.database import async_session_maker
from src.core.security import decode_token
from src.models.auth import TokenPayload
from src.services.auth import AuthService

http_bearer = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_service[T](service_cls: type[T]) -> Callable[[SessionDep], T]:
    def _factory(session: SessionDep) -> T:
        return service_cls(session)

    return _factory


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> uuid.UUID:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
        token_payload = TokenPayload(sub=sub)
    except (InvalidTokenError, ValueError):
        raise credentials_exception

    return token_payload.sub


AuthServiceDep = Annotated[AuthService, Depends(get_service(AuthService))]
LinkServiceDep = Annotated[LinkService, Depends(get_service(LinkService))]
UserIdDep = Annotated[uuid.UUID, Depends(get_current_user_id)]
