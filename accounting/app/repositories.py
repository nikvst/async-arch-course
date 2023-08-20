from decimal import Decimal
from typing import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Account, Transaction, User
from app.schemas import UserSchema


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User:
        stmt = select(User).where(User.id == user_id)
        return await self.session.scalar(stmt)

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


class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> Account:
        account = Account(
            user_id=user.id,
            balance=0,
        )
        self.session.add(account)
        await self.session.flush()

        return account

    async def get_by_user_id(self, user_id: UUID) -> Account:
        stmt = (
            select(Account)
            .options(joinedload(Account.user))
            .where(Account.user_id == user_id)
        )
        return await self.session.scalar(stmt)

    async def get_by_id(self, account_id: UUID) -> Account:
        stmt = (
            select(Account)
            .options(joinedload(Account.user))
            .where(Account.id == account_id)
        )
        return await self.session.scalar(stmt)

    async def update(self, account: Account, balance: Decimal) -> Account:
        account.balance = balance

        self.session.add(account)
        await self.session.flush()
        return account

    async def get_all(
        self,
        only_positive_balance: bool = False,
    ) -> Iterable[Account]:
        stmt = select(Account).options(joinedload(Account.user))
        if only_positive_balance is True:
            stmt = stmt.where(Account.balance > 0)

        result = await self.session.execute(stmt.order_by(Account.created_at.desc()))
        return result.scalars().all()


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, user_id: UUID, debt: Decimal, credit: Decimal, description: str
    ) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            debt=debt,
            credit=credit,
            description=description,
        )
        self.session.add(transaction)
        await self.session.flush()

        return transaction

    async def get_all(self, user_id: UUID) -> Iterable[Transaction]:
        stmt = select(Transaction).where(Transaction.user_id == user_id)
        return await self.session.scalar(stmt)
