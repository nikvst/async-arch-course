from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URI: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/task-tracker"
    ECHO_SQL: bool = True
    SECRET_KEY: str = "so_secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    KAFKA_BOOTSTRAP_SERVER: str = "localhost:29092"
    KAFKA_GROUP_ID: str = "task-tracker"
    USERS_STREAM_NAME: str = "users-stream"
    TASKS_STREAM_NAME: str = "tasks-stream"
    TOKEN_URL: str = "http://localhost:8001/token/"

    @computed_field
    @property
    def alembic_db_uri(self) -> str:
        return self.DB_URI.replace("+asyncpg", "")


settings = Settings.model_validate({})
