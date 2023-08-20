from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import UUID, Boolean, DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from app.constants import Role

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.WORKER)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    account: Mapped["Account"] = relationship(back_populates="user")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="account")
    balance: Mapped[Decimal]


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="transactions")
    debt: Mapped[Decimal] = mapped_column(default=0)
    credit: Mapped[Decimal] = mapped_column(default=0)
    description: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
