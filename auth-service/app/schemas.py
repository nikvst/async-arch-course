from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

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
