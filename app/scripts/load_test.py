import asyncio
from aiokafka import AIOKafkaProducer
import json
import time
from app.core.dependencies import get_settings_dependency


async def send_batch_messages(num_messages=1000, message_size=10000):
    settings = get_settings_dependency()
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    await producer.start()
    
    try:
        start_time = time.time()

        tasks = []
        for i in range(num_messages):
            message = {
                "id": i,
                "content": "X" * message_size,
                "timestamp": time.time()
            }
            tasks.append(producer.send(settings.KAFKA_MESSAGES_TOPIC, value=message))
            
            if i % 100 == 0:
                print(f"Created {i} send tasks...")

        await asyncio.gather(*tasks)
        
        end_time = time.time()
        print(f"Sent {num_messages} messages in {end_time - start_time:.2f} seconds")
    
    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(send_batch_messages())
