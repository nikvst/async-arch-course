from decimal import Decimal
from random import randint
from uuid import UUID

from app.constants import Role
from app.exceptions import TaskNotFoundError, UserNotFoundError
from app.models import User
from app.repositories import TaskRepository, UserRepository
from app.schemas import (
    CreateTaskRequestSchema,
    TaskSchema,
    UserSchema,
)
from app.use_cases._base import BaseSessionUseCase


class CreateTaskUseCase(BaseSessionUseCase):
    async def execute(self, task_data: CreateTaskRequestSchema) -> TaskSchema:
        task = await TaskRepository(self.session).create(
            title=task_data.title,
            description=task_data.description,
            cost=self._get_cost(),
            remuneration=self._get_remuneration(),
            assigned_to=await self._get_user(),
        )

        task_data = TaskSchema.model_validate(task)
        return task_data

    def _get_cost(self) -> Decimal:
        return Decimal(randint(10, 20))

    def _get_remuneration(self):
        return Decimal(randint(20, 40))

    async def _get_user(self) -> User:
        user = await UserRepository(self.session).get_random()
        if not user:
            raise UserNotFoundError()
        return user


class CompleteTaskUseCase(BaseSessionUseCase):
    async def execute(self, task_id: UUID, user: UserSchema) -> TaskSchema:
        ...


class ShuffleTasksUseCase(BaseSessionUseCase):
    async def execute(self) -> list[TaskSchema]:
        ...


class GetTasksUseCase(BaseSessionUseCase):
    async def execute(self, user: UserSchema) -> list[TaskSchema]:
        tasks = await TaskRepository(self.session).get_all(
            user_id=user.id if user.role not in (Role.ADMIN, Role.MANAGER) else None
        )
        return [TaskSchema.model_validate(task) for task in tasks]


class GetTaskUseCase(BaseSessionUseCase):
    async def execute(self, task_id: UUID, user: UserSchema) -> TaskSchema:
        task = await TaskRepository(self.session).get_by_id(task_id)
        if (
            not task
            or user.role not in (Role.ADMIN, Role.MANAGER)
            and task.assigned_to != user.id
        ):
            raise TaskNotFoundError()

        return TaskSchema.model_validate(task)
