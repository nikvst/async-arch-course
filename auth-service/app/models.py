from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import UUID, Boolean, DateTime, Enum, String, Uuid
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

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

    password_hash: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    modified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), onupdate=datetime.now
    )

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)
