from app.services.kafka_service import KafkaService
from app.core.config import Settings, get_settings
from typing import AsyncGenerator
from fastapi import Depends


def get_settings_dependency() -> Settings:
    return get_settings()


async def get_kafka_service(settings: Settings = Depends(get_settings_dependency)) \
        -> AsyncGenerator[KafkaService, None]:
    service = KafkaService(settings)
    try:
        yield service
    finally:
        await service.stop_producer()
