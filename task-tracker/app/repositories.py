from decimal import Decimal
from typing import Iterable
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.constants import Role
from app.models import Task, User
from app.schemas import UserSchema


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User:
        stmt = select(User).where(User.id == user_id)
        return await self.session.scalar(stmt)

    async def get_random(self) -> User:
        stmt = select(User).where(User.role.not_in([Role.ADMIN, Role.MANAGER]))
        return await self.session.scalar(stmt.order_by(func.random()))

    async def create(self, user_data: UserSchema) -> User:
        user = User(
            id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            role=user_data.role,
            is_active=user_data.is_active,
        )
        self.session.add(user)
        await self.session.flush()

        return user

    async def update(self, user: User, user_data: UserSchema) -> User:
        for key, value in user_data.model_dump().items():
            setattr(user, key, value)

        self.session.add(user)
        await self.session.flush()
        return user

    async def delete(self, user_id: UUID):
        stmt = delete(User).where(User.id == user_id)
        return await self.session.scalar(stmt)


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_id: UUID) -> Task:
        stmt = (
            select(Task).options(joinedload(Task.assigned_to)).where(Task.id == task_id)
        )
        return await self.session.scalar(stmt)

    async def get_all(self, user_id: UUID | None) -> Iterable[Task]:
        stmt = select(Task).options(joinedload(Task.assigned_to))
        if user_id:
            stmt = stmt.where(assigned_to=user_id)

        result = await self.session.execute(stmt.order_by(Task.created_at.desc()))
        return result.scalars().all()

    async def create(
        self,
        title: str,
        description: str,
        cost: Decimal,
        remuneration: Decimal,
        assigned_to: User,
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            cost=cost,
            remuneration=remuneration,
            assigned_to=assigned_to,
        )
        self.session.add(task)
        await self.session.flush()

        return task

    async def update(self, task: Task, completed: bool) -> Task:
        task.completed = completed

        self.session.add(task)
        await self.session.flush()
        return task
