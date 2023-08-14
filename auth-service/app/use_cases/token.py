from datetime import datetime, timedelta

from jose import jwt

from app.exceptions import UserNotFoundError, WrongPasswordError
from app.repositories import UserRepository
from app.schemas import TokenSchema, UserSchema
from app.settings import settings
from app.use_cases._base import BaseSessionUseCase


class AuthenticateUserUseCase(BaseSessionUseCase):
    async def execute(self, username: str, password: str) -> TokenSchema:
        user = await UserRepository(self.session).get_by_username(username)
        if not user:
            raise UserNotFoundError()

        if not user.verify_password(password):
            raise WrongPasswordError()

        user_obj = UserSchema.model_validate(user)
        claims = user_obj.model_dump(mode="json")
        claims["expire"] = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        token = jwt.encode(user_obj.model_dump(mode="json"), settings.SECRET_KEY)
        return TokenSchema(access_token=token, token_type="bearer")
