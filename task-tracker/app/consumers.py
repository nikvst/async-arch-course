import asyncio
import json
from logging import getLogger

import aiokafka

from app.constants import UserEvent
from app.db import async_session
from app.settings import settings
from app.use_cases.users import (
    CreateUserUseCase,
    DeleteUserUseCase,
    UpdateUserUseCase,
    UserRoleChangedUseCase,
)

logger = getLogger(__name__)

EVENT_HANDLERS = {
    UserEvent.USER_CREATED.value: CreateUserUseCase,
    UserEvent.USER_UPDATED.value: UpdateUserUseCase,
    UserEvent.USER_DELETED.value: DeleteUserUseCase,
    UserEvent.USER_ROLE_CHANGED.value: UserRoleChangedUseCase,
}


async def handle_message(msg):
    logger.info(f"Received new message from topic {msg.topic}: {msg}")

    if msg.topic == settings.USERS_STREAM_NAME:
        json_data = json.loads(msg.value)
        event_name = json_data.get("event_name")
        if event_name in EVENT_HANDLERS:
            async with async_session.begin() as session:
                handler = EVENT_HANDLERS[event_name](session=session)
                await handler.execute(json_data.get("data"))
        else:
            logger.info(f"Got unsupported event: {event_name}")


async def consume():
    consumer = aiokafka.AIOKafkaConsumer(
        settings.USERS_STREAM_NAME,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER,
        group_id=settings.KAFKA_GROUP_ID,
    )
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                await handle_message(msg)
            except Exception as e:
                logger.exception(f"raised unhandled error: {e}")

    finally:
        await consumer.stop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume())


if __name__ == "__main__":
    main()
