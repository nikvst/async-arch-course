import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
)

from app.constants import Role


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(validation_alias=AliasChoices("id", "public_id"))
    username: str
    email: str
    role: Role
    is_active: bool


class UserRoleChangedEventSchema(BaseModel):
    public_id: UUID
    role: Role


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None
    assigned_to: UserSchema
    title: str
    jira_id: str
    description: str
    completed: bool
    cost: Decimal
    remuneration: Decimal
    created_at: datetime
    modified_at: datetime | None


task_list_adapter = TypeAdapter(list[TaskSchema])


class CreateTaskRequestSchema(BaseModel):
    title: str
    jira_id: str = ""
    description: str

    @field_validator("title")
    @classmethod
    def title_must_not_contain_brackets(cls, v: str) -> str:
        if re.search(r"[\[\]]", v):
            raise ValueError("must not contain brackets")
        return v


class TaskCUEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(alias="id")
    assigned_to: UUID = Field(alias="assigned_to_id")
    title: str
    jira_id: str
    description: str
    completed: bool
    cost: float
    remuneration: float


class NewTaskCreatedEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(alias="id")
    assigned_to: UUID = Field(alias="assigned_to_id")
    title: str
    jira_id: str
    cost: float


class TaskAssignedEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(alias="id")
    assigned_to: UUID = Field(alias="assigned_to_id")
    title: str
    jira_id: str
    cost: float


class TaskCompletedEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(alias="id")
    assigned_to: UUID = Field(alias="assigned_to_id")
    title: str
    jira_id: str
    remuneration: float
