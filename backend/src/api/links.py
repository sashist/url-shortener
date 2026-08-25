from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter

from src.api.deps import LinkServiceDep, UserIdDep
from src.init import rabbit_manager
from src.models import ClickLogPublic, LinkCreate, LinkPublic, LinkUpdate


router = APIRouter(
    prefix="/links",
)

redirect_router = APIRouter(
    tags=["redirect"],
)


@router.post(
    "/", response_model=LinkPublic, tags=["links"], status_code=status.HTTP_201_CREATED
)
async def create_link(
    user_id: UserIdDep, link_data: LinkCreate, service: LinkServiceDep
) -> LinkPublic:
    new_link = await service.create_link(link_data, user_id)
    return new_link


@router.get("/", tags=["links"], response_model=list[LinkPublic])
async def get_links(user_id: UserIdDep, service: LinkServiceDep) -> list[LinkPublic]:
    links = await service.get_links_by_user_id(user_id)
    return links


@router.get("/{short_code}/stats", tags=["links"])
async def get_link_stats(
    short_code: str, user_id: UserIdDep, link_service: LinkServiceDep
) -> list[ClickLogPublic]:
    return await link_service.get_link_stats(short_code, user_id)


@router.patch("/{id}", response_model=LinkPublic, tags=["links"])
async def update_link(
    id: int, user_id: UserIdDep, link_service: LinkServiceDep, state: bool
) -> LinkPublic:
    return await link_service.update_link(id, user_id, state)


@redirect_router.get("/{short_code}")
async def redirect_to_url(short_code: str, service: LinkServiceDep, request: Request):
    link = await service.get_by_short_code(short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await rabbit_manager.publish_event(
        routing_key="link.clicked",
        payload={
            "link_id": link.id,
            "browser": request.headers.get("user-agent"),
            "country": request.headers.get("cf-ipcountry")
            or request.headers.get("x-country-code"),
        },
    )
    return RedirectResponse(url=str(link.original_url))
