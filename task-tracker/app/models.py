from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import UUID, Boolean, DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from app.constants import Role
from app.utils import verify_password

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.WORKER)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    assigned_tasks: Mapped[list["Task"]] = relationship(back_populates="assigned_to")

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    assigned_to_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    assigned_to: Mapped["User"] = relationship(back_populates="assigned_tasks")
    title: Mapped[str]
    description: Mapped[str] = mapped_column(default=True)
    completed: Mapped[bool] = mapped_column(default=False)
    cost: Mapped[Decimal]
    remuneration: Mapped[Decimal]

    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    modified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), onupdate=datetime.now
    )

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)
