import uuid
from collections.abc import Sequence

from pydantic import BaseModel
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession


class BaseRepository[ModelType: SQLModel]:
    model: type[ModelType]
    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, db_obj: ModelType) -> ModelType:
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def add_bulk(self, db_objs: Sequence[ModelType]) -> list[ModelType]:
        self.session.add_all(db_objs)
        await self.session.flush()

    async def get_one(self, id: uuid.UUID) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def get_all(self) -> list[ModelType]:
        return await self.get_filtered()

    async def get_filtered(self, **kwargs) -> list[ModelType]:
        statement = select(self.model).filter_by(**kwargs)
        query = await self.session.exec(statement)
        return query.all()

    async def update(self, db_obj: ModelType, data: BaseModel) -> ModelType:
        updated_data = data.model_dump(exclude_unset=True)
        db_obj.sqlmodel_update(updated_data)
        await self.session.flush()
        return db_obj

    async def delete(self, db_obj: ModelType) -> ModelType:
        await self.session.delete(db_obj)
        await self.session.flush()
        return db_obj
