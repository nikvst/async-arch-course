from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session


class BaseSessionUseCase:
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def execute(self, *args, **kwargs) -> None:
        raise NotImplementedError()
