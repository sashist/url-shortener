from fastapi import APIRouter, Request, Response, status

from src.api.deps import AuthServiceDep, UserIdDep
from src.models.auth import Token
from src.models.users import UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register(service: AuthServiceDep, data: UserCreate) -> UserPublic:
    user = await service.register_user(data)
    return user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    service: AuthServiceDep,
    data: UserCreate,
    response: Response,
) -> Token:
    access_token, refresh_token = await service.login_user(data)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=Token)
async def refresh(
    request: Request,
    response: Response,
    service: AuthServiceDep,
) -> Token:
    refresh_token = request.cookies.get("refresh_token")
    new_access, new_refresh = await service.refresh_tokens(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return Token(access_token=new_access, token_type="bearer")


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserPublic)
async def get_me(user_id: UserIdDep, service: AuthServiceDep) -> UserPublic:
    user = await service.get_user_by_id(str(user_id))
    return user
