from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import UserEvent
from app.db import get_session
from app.exceptions import UserNotFoundError
from app.repositories import UserRepository
from app.schemas import (
    CreateUserRequestSchema,
    UpdateUserRequestSchema,
    UserCUEventSchema,
    UserSchema,
)
from app.settings import settings
from app.use_cases._base import BaseSessionUseCase
from app.use_cases.kafka import SentEventToKafkaUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
    async def execute(self, data: CreateUserRequestSchema) -> UserSchema:
        user = await UserRepository(self.session).create(
            username=data.username, password=data.password, email=data.email
        )
        user_data = UserSchema.model_validate(user)

        await SentEventToKafkaUseCase().execute(
            settings.USERS_STREAM_TOPIC_NAME,
            UserEvent.USER_CREATED,
            1,
            UserCUEventSchema.model_validate(user_data),
        )
        return user_data


class UpdateUserUseCase(BaseSessionUseCase):
    async def execute(
        self, user_data: UserSchema, data: UpdateUserRequestSchema
    ) -> UserSchema:
        user = await UserRepository(self.session).get_by_id(user_data.id)
        if not user:
            raise UserNotFoundError()

        user = await UserRepository(self.session).update(user, data)
        user_data = UserSchema.model_validate(user)
        await SentEventToKafkaUseCase().execute(
            settings.USERS_STREAM_TOPIC_NAME,
            UserEvent.USER_UPDATED,
            1,
            UserCUEventSchema.model_validate(user_data),
        )
        return user_data
