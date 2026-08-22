import uuid
from datetime import datetime

from pydantic import HttpUrl
from sqlmodel import AutoString, DateTime, Field, SQLModel

from src.utils import get_datetime_utc


class LinkBase(SQLModel):
    original_url: str
    is_active: bool = Field(default=True)


class LinkCreate(SQLModel):
    original_url: HttpUrl


class LinkPublic(LinkBase):
    id: int
    short_code: str


class LinkUpdate(SQLModel):
    original_url: HttpUrl | None = None
    is_active: bool | None = None


class Link(LinkBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    short_code: str | None = Field(index=True, unique=True, max_length=10, default=None)
    is_active: bool = Field(default=True)
    user_id: uuid.UUID | None = Field(
        foreign_key="user.id", default=None, nullable=True
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc, sa_type=DateTime(timezone=True)
    )
