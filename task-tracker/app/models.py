from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

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
    assigned_tasks: Mapped[list["Task"]] = relationship(back_populates="assigned_to")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    assigned_to_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    assigned_to: Mapped["User"] = relationship(back_populates="assigned_tasks")
    title: Mapped[str]
    jira_id: Mapped[str] = mapped_column(default="")
    description: Mapped[str] = mapped_column(default="")
    completed: Mapped[bool] = mapped_column(default=False)
    cost: Mapped[Decimal]
    remuneration: Mapped[Decimal]

    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    modified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), onupdate=datetime.now
    )
