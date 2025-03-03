import json
import logging
from aiokafka import AIOKafkaConsumer
from app.core.config import get_settings
from typing import Optional


logger = logging.getLogger("app.services.message_consumer")


class MessageConsumer:
    def __init__(self):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.should_stop = False
        self.settings = get_settings()

    async def start(self, group_id: str = "message_group"):
        if self.consumer is None:
            logger.info("Starting Kafka consumer...")
            self.consumer = AIOKafkaConsumer(
                self.settings.KAFKA_MESSAGES_TOPIC,
                bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest'
            )
            await self.consumer.start()
            logger.info("Kafka consumer started successfully")

    async def stop(self):
        if self.consumer:
            logger.info("Stopping Kafka consumer...")
            self.should_stop = True
            await self.consumer.stop()
            self.consumer = None
            logger.info("Kafka consumer stopped successfully")

    async def consume_messages(self):
        if not self.consumer:
            logger.error("Consumer not initialized")
            return

        logger.info("Starting to consume messages...")
        try:
            async for message in self.consumer:
                if self.should_stop:
                    break
                    
                try:
                    logger.info(
                        f"Received message: {message.value} "
                        f"from topic {message.topic} "
                        f"at partition {message.partition} "
                        f"with offset {message.offset}"
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            await self.stop()
