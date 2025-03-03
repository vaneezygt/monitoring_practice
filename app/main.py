from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.api.endpoints import message, user, auth
from app.db.database import get_engine
from app.services.kafka_service import KafkaService
from app.services.message_consumer import MessageConsumer
from app.core.error_handlers import add_error_handlers
from app.core.dependencies import get_settings_dependency
from app.core.logging_config import setup_logging
from typing import AsyncGenerator
import asyncio


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    # Setup logging
    setup_logging()
    
    # Get settings from dependency
    settings = get_settings_dependency()
    engine = get_engine(settings)
    
    # Initialize Kafka service
    kafka_service = KafkaService(settings)
    await kafka_service.start_producer()
    
    # Initialize and start consumer
    consumer = MessageConsumer()
    await consumer.start()
    
    # Start consuming messages in background task
    consumer_task = asyncio.create_task(consumer.consume_messages())
    
    yield
    
    # Shutdown: Clean up resources
    await consumer.stop()
    await consumer_task
    await kafka_service.stop_producer()
    await engine.dispose()


def create_app() -> FastAPI:
    # Get settings first
    settings = get_settings_dependency()
    
    fastapi_app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
        dependencies=[Depends(get_settings_dependency)]
    )
    
    # Add error handlers
    add_error_handlers(fastapi_app)
    
    # Include routers
    fastapi_app.include_router(
        message.router,
        prefix=settings.API_V1_STR,
        tags=["messages"]
    )
    fastapi_app.include_router(
        user.router,
        prefix=settings.API_V1_STR,
        tags=["users"]
    )
    fastapi_app.include_router(
        auth.router,
        prefix=f"{settings.API_V1_STR}/auth",
        tags=["auth"]
    )
    
    return fastapi_app


app = create_app()


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Kafka App"}
