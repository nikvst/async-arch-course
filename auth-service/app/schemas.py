from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.constants import Role


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None
    username: str
    email: str
    role: Role
    is_active: bool
    created_at: datetime
    modified_at: datetime | None


class CreateUserRequestSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UpdateUserRequestSchema(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserCUEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(alias="id")
    username: str
    email: str
    role: Role
    is_active: bool


class UserRoleChangedEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(alias="id")
    role: Role
