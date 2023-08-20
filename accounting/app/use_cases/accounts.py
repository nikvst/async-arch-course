from uuid import UUID

from app.constants import TransactionEvent
from app.exceptions import AccountNotFoundError
from app.repositories import AccountRepository, TransactionRepository
from app.schemas import (
    AccountSchema,
    TransactionCreatedEventSchema,
    TransactionSchema,
    UserSchema,
)
from app.settings import settings
from app.use_cases._base import BaseSessionUseCase
from app.use_cases.kafka import SentEventToKafkaUseCase


class CloseCurrentDayUseCase(BaseSessionUseCase):
    async def execute(self, *args, **kwargs) -> None:
        accounts = await AccountRepository(self.session).get_all(
            only_positive_balance=True
        )
        for account in accounts:
            user = account.user
            transaction = await TransactionRepository(self.session).create(
                user_id=user.id,
                credit=account.balance,
                debt=0,
                description="Выплата за период",
            )
            await AccountRepository(self.session).update(account, 0)

            await SentEventToKafkaUseCase().execute(
                settings.TRANSACTIONS_STREAM_TOPIC_NAME,
                TransactionEvent.TRANSACTION_CREATED,
                1,
                TransactionCreatedEventSchema.model_validate(transaction),
            )

            # TODO: send email to user


class GetUserAccountsUseCase(BaseSessionUseCase):
    async def execute(self) -> list[AccountSchema]:
        accounts = await AccountRepository(self.session).get_all()
        return [AccountSchema.model_validate(account) for account in accounts]


class GetUserAccountUseCase(BaseSessionUseCase):
    async def execute(self, account_id: UUID | str, user: UserSchema) -> AccountSchema:
        if account_id == "my":
            account = await AccountRepository(self.session).get_by_id(account_id)
        else:
            account = await AccountRepository(self.session).get_by_user_id(user.id)

        if not account:
            raise AccountNotFoundError()

        return AccountSchema.model_validate(account)


class GetTransactionsUseCase(BaseSessionUseCase):
    async def execute(
        self, account_id: UUID | str, user: UserSchema
    ) -> list[TransactionSchema]:
        account_data = await GetUserAccountUseCase(self.session).execute(
            account_id, user
        )
        transactions = await TransactionRepository(self.session).get_all(
            account_data.user.id
        )
        return [
            TransactionSchema.model_validate(transaction)
            for transaction in transactions
        ]
