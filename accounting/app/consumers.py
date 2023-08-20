import asyncio
import json
from logging import getLogger

import aiokafka
from schema_registry import validate_schema

from app.constants import TaskEvent, UserEvent
from app.db import async_session
from app.settings import settings
from app.use_cases.tasks import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    NewTaskCreatedUseCase,
)
from app.use_cases.users import (
    CreateUserUseCase,
    UpdateUserUseCase,
)

logger = getLogger(__name__)

EVENT_HANDLERS = {
    UserEvent.USER_CREATED.value: {1: CreateUserUseCase},
    UserEvent.USER_UPDATED.value: {1: UpdateUserUseCase},
    TaskEvent.TASK_COMPLETED.value: {2: CompleteTaskUseCase},
    TaskEvent.TASK_ASSIGNED: {2: AssignTaskUseCase},
    TaskEvent.TASK_NEW_TASK_CREATED: {2: NewTaskCreatedUseCase},
}


async def handle_message(msg):
    logger.info(f"Received new message from topic {msg.topic}: {msg}")

    if msg.topic in (
        settings.USERS_STREAM_TOPIC_NAME,
        settings.TASKS_FLOW_TOPIC_NAME,
    ):
        json_data = json.loads(msg.value)
        event_name = json_data.get("event_name")
        event_version = json_data.get("event_version")

        if event_name not in EVENT_HANDLERS:
            logger.info(f"Got unsupported event: {event_name}")
            return

        if event_version not in EVENT_HANDLERS[event_name]:
            logger.info(
                f"Got unsupported event version: {event_name}, v{event_version}"
            )
            return

        validate_schema(json_data, event_name, event_version)

        handler = EVENT_HANDLERS[event_name][event_version]
        async with async_session.begin() as session:
            handler = handler(session=session)
            await handler.execute(json_data.get("data"))


async def consume():
    consumer = aiokafka.AIOKafkaConsumer(
        settings.USERS_STREAM_TOPIC_NAME,
        settings.TASKS_FLOW_TOPIC_NAME,
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
