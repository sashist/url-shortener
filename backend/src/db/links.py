import uuid
from datetime import datetime

from sqlmodel import DateTime, Field, SQLModel

from src.utils import get_datetime_utc


class LinkBase(SQLModel):
    original_url: str


class LinkCreate(LinkBase):
    pass


class LinkPublic(LinkBase):
    id: uuid.UUID
    short_code: str
    is_active: bool


class LinkUpdate(SQLModel):
    original_url: str | None = None
    is_active: bool | None = None


class Link(LinkBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    short_code: str = Field(index=True, unique=True, max_length=10)
    is_active: bool = Field(default=True)
    user_id: uuid.UUID | None = Field(
        foreign_key="user.id", default=None, nullable=True
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc, sa_type=DateTime(timezone=True)
    )
