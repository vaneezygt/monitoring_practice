from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.core.config import Settings
import json
from typing import Any, Dict
import logging
import asyncio
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

logger = logging.getLogger(__name__)


class KafkaService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.producer = None
        self.consumer = None
        self.topic = settings.KAFKA_MESSAGES_TOPIC

    async def create_topic(self, topic_name: str, num_partitions: int = 1, replication_factor: int = 1) -> None:
        """
        Create a Kafka topic with specified number of partitions
        """
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, self._create_topic_sync,
                                       topic_name, num_partitions, replication_factor)
        except Exception as e:
            logger.error(f"Error creating topic {topic_name}: {e}")
            raise

    def _create_topic_sync(self, topic_name: str, num_partitions: int, replication_factor: int) -> None:
        """
        Synchronous implementation of topic creation to be run in executor
        """
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='admin'
            )

            topic_list = [
                NewTopic(
                    name=topic_name,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor
                )
            ]

            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            logger.info(f"Topic {topic_name} created with {num_partitions} partitions")
            admin_client.close()
        except TopicAlreadyExistsError:
            logger.info(f"Topic {topic_name} already exists")
        except Exception as e:
            logger.error(f"Error in _create_topic_sync: {e}")
            raise

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

            await self.create_topic(
                self.settings.KAFKA_MESSAGES_TOPIC,
                num_partitions=self.settings.KAFKA_TOPIC_PARTITIONS,
            )

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
