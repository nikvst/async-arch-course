from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, TypeAdapter

from app.constants import Role


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str
    role: Role
    is_active: bool


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None
    assigned_to: UserSchema
    title: str
    description: str
    completed: bool
    cost: Decimal
    remuneration: Decimal
    created_at: datetime
    modified_at: datetime | None


task_list_adapter = TypeAdapter(list[TaskSchema])


class CreateTaskRequestSchema(BaseModel):
    title: str
    description: str
