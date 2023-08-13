import json

import aiokafka
from pydantic import BaseModel

from app.settings import settings


class SentEventToKafkaUseCase:
    def execute(self, topic_name: str, event_name: str, data: dict | BaseModel) -> None:
        if isinstance(data, BaseModel):
            data = data.model_dump(mode="json")
        event_data = {
            "event_name": event_name,
            "data": data,
        }
        event_data_encoded = json.dumps(event_data).encode("utf-8")

        producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER,
            client_id=settings.KAFKA_CLIENT_ID,
        )
        await producer.start()
        try:
            await producer.send_and_wait(topic_name, event_data_encoded)
        finally:
            await producer.stop()
