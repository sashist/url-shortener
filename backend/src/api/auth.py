from fastapi import APIRouter, HTTPException, Request, Response, status

from src.api.deps import AuthServiceDep, UserIdDep
from src.core.security import create_access_token, create_refresh_token, decode_token
from src.db.auth import Token
from src.db.users import UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register(service: AuthServiceDep, data: UserCreate) -> UserPublic:
    user = await service.register_user(data)
    return user


@router.post("/login")
async def login(service: AuthServiceDep, response: Response, data: UserCreate) -> Token:
    access_token, refresh_token = await service.login_user(data.email, data.password)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict",
        secure=True,
    )
    return Token(access_token=access_token, token_type="bearer")

async def logout(response: Response):
    response.delete_cookie(key="refresh_token", httponly=True, samesite="strict", secure=True)
    return {"message": "Logged out successfully"}

@router.post("/refresh", response_model=Token)
async def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token(data={"sub": payload["sub"]})
    new_refresh = create_refresh_token(data={"sub": payload["sub"]})

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return Token(access_token=new_access, token_type="bearer")


@router.get("/me", response_model=UserPublic)
async def get_me(user_id: UserIdDep, service: AuthServiceDep) -> UserPublic:
    user = await service.get_user_by_id(user_id)
    return user
