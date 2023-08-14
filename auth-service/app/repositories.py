from uuid import UUID

from asyncpg import UniqueViolationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Role
from app.exceptions import UserAlreadyExistsError
from app.models import User
from app.schemas import UpdateUserRequestSchema
from app.utils import get_password_hash


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User:
        stmt = select(User).where(User.id == user_id)
        return await self.session.scalar(stmt)

    async def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        return await self.session.scalar(stmt)

    async def create(
        self, username: str, email: str, password: str, role=Role.WORKER
    ) -> User:
        password_hash = get_password_hash(password)

        user = User(
            username=username,
            email=email,
            role=role,
            password_hash=password_hash,
        )
        self.session.add(user)

        try:
            await self.session.flush()
        except IntegrityError as e:
            if e.orig.pgcode == UniqueViolationError.sqlstate:
                raise UserAlreadyExistsError() from e
            else:
                raise e

        return user

    async def update(self, user: User, data: UpdateUserRequestSchema):
        if data.password:
            data.password = get_password_hash(data.password)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        self.session.add(user)
        try:
            await self.session.flush()
        except IntegrityError as e:
            if e.orig.pgcode == UniqueViolationError.sqlstate:
                raise UserAlreadyExistsError() from e
            else:
                raise e

        return user
