from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URI: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/auth"
    ECHO_SQL: bool = True
    SECRET_KEY: str = "so_secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    KAFKA_BOOTSTRAP_SERVER: str = "localhost:29092"
    KAFKA_GROUP_ID: str = "auth-service"
    USERS_STREAM_NAME: str = "users-stream"

    @computed_field
    @property
    def alembic_db_uri(self) -> str:
        return self.DB_URI.replace("+asyncpg", "")


settings = Settings.model_validate({})
