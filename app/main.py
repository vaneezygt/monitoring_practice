from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from typing import AsyncGenerator

from app.api.endpoints import message, user, auth
from app.db.database import get_engine
from app.services.kafka_service import KafkaService
from app.core.error_handlers import add_error_handlers
from app.core.dependencies import get_settings_dependency
from app.core.logging_config import setup_logging
from app.services.multiple_consumers import MultipleConsumersService


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
    
    # Initialize and start multiple consumers
    multiple_consumers = MultipleConsumersService(num_consumers=settings.KAFKA_TOPIC_PARTITIONS)
    await multiple_consumers.start()
    
    yield
    
    # Shutdown: Clean up resources
    await multiple_consumers.stop()
    await kafka_service.stop_producer()
    await engine.dispose()


def init_app() -> FastAPI:
    """Initialize FastAPI application."""
    settings = get_settings_dependency()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
        dependencies=[Depends(get_settings_dependency)]
    )
    
    # Add error handlers
    add_error_handlers(app)
    
    # Include routers
    app.include_router(
        message.router,
        prefix=settings.API_V1_STR,
        tags=["messages"]
    )
    app.include_router(
        user.router,
        prefix=settings.API_V1_STR,
        tags=["users"]
    )
    app.include_router(
        auth.router,
        prefix=f"{settings.API_V1_STR}/auth",
        tags=["auth"]
    )
    
    return app
