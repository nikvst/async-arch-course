import json
import uuid
from datetime import datetime

import aiokafka
from pydantic import BaseModel
from schema_registry import validate_schema

from app.constants import UserEvent
from app.settings import settings


class SentEventToKafkaUseCase:
    async def execute(
        self,
        topic_name: str,
        event_name: UserEvent,
        version: int,
        data: dict | BaseModel,
    ) -> None:
        if isinstance(data, BaseModel):
            data = data.model_dump(mode="json")

        event_data = {
            "event_id": str(uuid.uuid4()),
            "event_version": version,
            "event_time": datetime.now().isoformat(),
            "producer": settings.SERVICE_NAME,
            "event_name": event_name.value,
            "data": data,
        }

        validate_schema(event_data, event_name, version)

        producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER
        )
        await producer.start()
        try:
            await producer.send_and_wait(
                topic_name,
                json.dumps(event_data).encode("utf-8"),
            )
        finally:
            await producer.stop()
