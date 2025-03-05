from aiokafka import AIOKafkaConsumer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
import asyncio
from typing import List
from app.core.dependencies import get_settings_dependency
import logging


class MultipleConsumersService:
    def __init__(self, num_consumers=3):
        self.num_consumers = num_consumers
        self.consumers: List[AIOKafkaConsumer] = []
        self.tasks: List[asyncio.Task] = []
        self.settings = get_settings_dependency()
        
    async def ensure_topic_exists(self):
        admin_client = AIOKafkaAdminClient(
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id='admin-setup'
        )
        
        try:
            await admin_client.start()
            topics = await admin_client.list_topics()
            
            if self.settings.KAFKA_MESSAGES_TOPIC not in topics:
                topic = NewTopic(
                    name=self.settings.KAFKA_MESSAGES_TOPIC,
                    num_partitions=self.num_consumers,
                    replication_factor=1
                )
                await admin_client.create_topics([topic])
                logging.info(f"Created topic {self.settings.KAFKA_MESSAGES_TOPIC} with {self.num_consumers} partitions")
            else:
                logging.info(f"Topic {self.settings.KAFKA_MESSAGES_TOPIC} already exists")
                
        finally:
            await admin_client.close()

    async def consume_messages(self, consumer_id):
        consumer = AIOKafkaConsumer(
            self.settings.KAFKA_MESSAGES_TOPIC,
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id='message_group',
            auto_offset_reset='earliest'
        )
        
        self.consumers.append(consumer)
        await consumer.start()
        
        print(f"Consumer {consumer_id} started")
        try:
            async for message in consumer:
                print(f"Consumer {consumer_id} received: {message.value.decode('utf-8')}")
        finally:
            await consumer.stop()

    async def start(self):
        await self.ensure_topic_exists()
        
        for i in range(self.num_consumers):
            task = asyncio.create_task(self.consume_messages(i))
            self.tasks.append(task)
        
        print(f"Started {self.num_consumers} consumers")

    async def stop(self):
        print("Stopping consumers...")
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        for consumer in self.consumers:
            await consumer.stop()
