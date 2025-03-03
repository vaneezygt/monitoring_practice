from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from app.core.exceptions import MessageNotFoundError, KafkaError, DatabaseError

logger = logging.getLogger(__name__)


async def message_not_found_handler(_: Request, exc: MessageNotFoundError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def kafka_error_handler(_: Request, exc: KafkaError):
    logger.error(f"Kafka error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def database_error_handler(_: Request, exc: DatabaseError):
    logger.error(f"Database error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


def add_error_handlers(app):
    app.add_exception_handler(MessageNotFoundError, message_not_found_handler)
    app.add_exception_handler(KafkaError, kafka_error_handler)
    app.add_exception_handler(DatabaseError, database_error_handler)
