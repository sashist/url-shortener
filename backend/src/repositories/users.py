from pydantic import EmailStr
from sqlmodel import select

from src.models.users import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_user_with_hash_password(self, email: EmailStr) -> User | None:
        statement = select(self.model).filter_by(email=email)
        query = await self.session.exec(statement)
        return query.one_or_none()
