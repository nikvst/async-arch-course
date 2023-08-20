from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

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


class NewTaskCreatedEventSchema(BaseModel):
    public_id: UUID
    assigned_to: UUID
    title: str
    jira_id: str
    cost: Decimal


class TaskAssignedEventSchema(BaseModel):
    public_id: UUID
    assigned_to: UUID
    title: str
    jira_id: str
    cost: Decimal


class TaskCompletedEventSchema(BaseModel):
    public_id: UUID
    assigned_to: UUID
    title: str
    jira_id: str
    remuneration: Decimal


class AccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user: UserSchema
    balance: Decimal


class TransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    debt: Decimal
    credit: Decimal
    description: str
    created_at: datetime


class TransactionCreatedEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(alias="id")
    user: UUID = Field(alias="user_id")
    debt: float
    credit: float
    description: str
    created_at: str

    @field_validator("created_at", mode="before")
    @classmethod
    def created_at_as_str(cls, v: datetime) -> str:
        return v.isoformat()
