from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.links import router as link_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(link_router)
