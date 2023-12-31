from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Role
from app.db import get_session
from app.exceptions import UserNotFoundError
from app.repositories import UserRepository
from app.schemas import (
    UserRoleChangedEventSchema,
    UserSchema,
)
from app.settings import settings
from app.use_cases._base import BaseSessionUseCase
from app.use_cases.tasks import ShuffleTasksUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


async def get_current_user(
    session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> UserSchema:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = await UserRepository(session).get_by_id(payload.get("id"))
        if not user:
            raise UserNotFoundError("User not found")
        return UserSchema.model_validate(user)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=str(e),
        ) from e


class CreateUserUseCase(BaseSessionUseCase):
    async def execute(self, user_event_data: dict) -> None:
        user_data = UserSchema.model_validate(user_event_data)
        await UserRepository(self.session).create(user_data)


class UpdateUserUseCase(BaseSessionUseCase):
    async def execute(self, user_event_data: dict) -> None:
        user_data = UserSchema.model_validate(user_event_data)
        user = await UserRepository(self.session).get_by_id(user_data.id)
        if user:
            await UserRepository(self.session).update(user, user_data)
        else:
            await UserRepository(self.session).create(user_data)


class UserRoleChangedUseCase(BaseSessionUseCase):
    async def execute(self, user_event_data: dict) -> None:
        user_data = UserRoleChangedEventSchema.model_validate(user_event_data)
        if user_data.role not in (Role.ADMIN, Role.MANAGER):
            return

        await ShuffleTasksUseCase(self.session).execute(user_data.public_id)
