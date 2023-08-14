from decimal import Decimal
from random import randint
from uuid import UUID

from app.constants import Role, TaskEvent
from app.exceptions import (
    OnlyAssignedUserCanCompleteTaskError,
    TaskNotFoundError,
    UserNotFoundError,
)
from app.models import Task, User
from app.repositories import TaskRepository, UserRepository
from app.schemas import (
    CreateTaskRequestSchema,
    TaskSchema,
    UserSchema,
)
from app.settings import settings
from app.use_cases._base import BaseSessionUseCase
from app.use_cases.kafka import SentEventToKafkaUseCase


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

        SentEventToKafkaUseCase().execute(
            settings.TASKS_STREAM_NAME, TaskEvent.TASK_CREATED, task_data
        )
        SentEventToKafkaUseCase().execute(
            settings.TASKS_STREAM_NAME, TaskEvent.TASK_ASSIGNED, task_data
        )

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
        task = await TaskRepository(self.session).get_by_id(task_id)
        if not task:
            raise TaskNotFoundError()

        if task.assigned_to_id != user.id:
            raise OnlyAssignedUserCanCompleteTaskError()

        task = await TaskRepository(self.session).update(task=task, completed=True)

        task_data = TaskSchema.model_validate(task)

        SentEventToKafkaUseCase().execute(
            settings.TASKS_STREAM_NAME, TaskEvent.TASK_UPDATED, task_data
        )
        SentEventToKafkaUseCase().execute(
            settings.TASKS_STREAM_NAME, TaskEvent.TASK_COMPLETED, task_data
        )
        return task_data


class ShuffleTasksUseCase(BaseSessionUseCase):
    async def execute(self, user: UserSchema | None = None) -> list[TaskSchema]:
        tasks = await TaskRepository(self.session).get_all(
            completed=False,
            user_id=user and user.id,
        )

        tasks_data = []

        for task in tasks:
            tasks_data.append(await self._reassign_task(task))

        return tasks_data

    async def _get_user(self) -> User:
        user = await UserRepository(self.session).get_random()
        if not user:
            raise UserNotFoundError()
        return user

    async def _reassign_task(self, task: Task) -> TaskSchema:
        task = await TaskRepository(self.session).update(
            task, assigned_to=await self._get_user()
        )

        task_data = TaskSchema.model_validate(task)

        SentEventToKafkaUseCase().execute(
            settings.TASKS_STREAM_NAME, TaskEvent.TASK_UPDATED, task_data
        )
        SentEventToKafkaUseCase().execute(
            settings.TASKS_STREAM_NAME, TaskEvent.TASK_ASSIGNED, task_data
        )

        return task_data


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
