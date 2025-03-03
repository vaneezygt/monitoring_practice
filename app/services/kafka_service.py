from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.core.config import Settings
import json
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class KafkaService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.producer = None
        self.consumer = None
        self.topic = settings.KAFKA_MESSAGES_TOPIC

    async def start_producer(self) -> None:
        if not self.producer:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='producer',
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version='auto'
            )
            await self.producer.start()
            logger.info("Kafka producer started")

    async def stop_producer(self) -> None:
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("Kafka producer stopped")
            except Exception as e:
                logger.error(f"Error stopping producer: {e}")
            finally:
                self.producer = None

    async def send_message(self, message: Dict[str, Any]) -> None:
        if not self.producer:
            await self.start_producer()
        try:
            await self.producer.send_and_wait(self.topic, message)
            logger.info(f"Message sent to Kafka: {message}")
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {e}")
            raise

    async def start_consumer(self, group_id: str) -> None:
        if not self.consumer:
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=group_id,
                client_id='consumer',
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                api_version='auto'
            )
            await self.consumer.start()
            logger.info("Kafka consumer started")

    async def stop_consumer(self) -> None:
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None
            logger.info("Kafka consumer stopped")
