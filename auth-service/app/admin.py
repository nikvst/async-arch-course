from sqladmin import ModelView

from app.constants import UserEvent
from app.models import User
from app.repositories import UserRepository
from app.schemas import UserSchema
from app.settings import settings
from app.use_cases.kafka import SentEventToKafkaUseCase
from app.utils import get_password_hash


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.is_active]
    is_async = True

    async def on_model_change(self, data: dict, model: User, is_created: bool) -> None:
        self._role_was_changed = False
        if is_created is False and data["role"] != model.role.name:
            self._role_was_changed = True

        if data["password_hash"] != model.password_hash:
            data["password_hash"] = get_password_hash(data["password_hash"])

    async def after_model_change(
        self, data: dict, model: User, is_created: bool
    ) -> None:
        """Юзеры могут изменяться как через api, так и через админку.
        При апдейте из админки также будет отправлять сигналы.
        """
        async with self.session_maker(expire_on_commit=False) as session:
            user = await UserRepository(session).get_by_id(model.id)
            user_data = UserSchema.model_validate(user)

        await SentEventToKafkaUseCase().execute(
            settings.USERS_STREAM_TOPIC_NAME,
            UserEvent.USER_CREATED if is_created else UserEvent.USER_UPDATED,
            user_data,
        )
        if self._role_was_changed:
            await SentEventToKafkaUseCase().execute(
                settings.USERS_ROLE_CHANGED_TOPIC_NAME,
                UserEvent.USER_ROLE_CHANGED,
                user_data,
            )

    async def after_model_delete(self, model: User) -> None:
        """Единственный способ удалить пользователя - через админку."""
        await SentEventToKafkaUseCase().execute(
            settings.USERS_STREAM_TOPIC_NAME, UserEvent.USER_DELETED, {"id": model.id}
        )
