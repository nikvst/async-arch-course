from pydantic import BaseModel

from app.constants import TransactionEvent
from app.repositories import AccountRepository, TransactionRepository, UserRepository
from app.schemas import (
    NewTaskCreatedEventSchema,
    TaskAssignedEventSchema,
    TaskCompletedEventSchema,
    TransactionCreatedEventSchema,
)
from app.settings import settings
from app.use_cases._base import BaseSessionUseCase
from app.use_cases.kafka import SentEventToKafkaUseCase


class CompleteTaskUseCase(BaseSessionUseCase):
    async def execute(self, event_data: dict) -> None:
        data = TaskCompletedEventSchema.model_validate(event_data)

        user = await UserRepository(self.session).get_by_id(data.assigned_to)
        account = await AccountRepository(self.session).get_by_user_id(user.id)

        await AccountRepository(self.session).update(
            account, balance=account.balance + data.remuneration
        )
        transaction = await TransactionRepository(self.session).create(
            user_id=user.id,
            debt=data.remuneration,
            credit=0,
            description=f'Начисление средств за выполнение задачи "{data.title}" (id: {data.public_id})',
        )

        await SentEventToKafkaUseCase().execute(
            settings.TRANSACTIONS_STREAM_TOPIC_NAME,
            TransactionEvent.TRANSACTION_CREATED,
            1,
            TransactionCreatedEventSchema.model_validate(transaction),
        )


class BaseAssignTaskUseCase(BaseSessionUseCase):
    async def execute(self, event_data: dict) -> None:
        data = self._get_data(event_data)

        user = await UserRepository(self.session).get_by_id(data.assigned_to)
        account = await AccountRepository(self.session).get_by_user_id(user.id)

        await AccountRepository(self.session).update(
            account, balance=account.balance - data.cost
        )
        transaction = await TransactionRepository(self.session).create(
            user_id=user.id,
            debt=0,
            credit=data.cost,
            description=f'Списание средств за назначение задачи "{data.title}" (id: {data.public_id})',
        )

        await SentEventToKafkaUseCase().execute(
            settings.TRANSACTIONS_STREAM_TOPIC_NAME,
            TransactionEvent.TRANSACTION_CREATED,
            1,
            TransactionCreatedEventSchema.model_validate(transaction),
        )

    def _get_data(self, event_data: dict) -> BaseModel:
        raise NotImplementedError()


class AssignTaskUseCase(BaseAssignTaskUseCase):
    def _get_data(self, event_data: dict) -> TaskAssignedEventSchema:
        return TaskAssignedEventSchema.model_validate(event_data)


class NewTaskCreatedUseCase(BaseAssignTaskUseCase):
    def _get_data(self, event_data: dict) -> NewTaskCreatedEventSchema:
        return NewTaskCreatedEventSchema.model_validate(event_data)
