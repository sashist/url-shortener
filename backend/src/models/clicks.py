import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from src.utils import get_datetime_utc


class ClickLogBase(SQLModel):
    link_id: int | None
    country: str | None = None
    browser: str | None = None


class ClickLogPublic(ClickLogBase):
    id: uuid.UUID
    created_at: datetime | None = None


class ClickLog(ClickLogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc, sa_type=DateTime(timezone=True)
    )
