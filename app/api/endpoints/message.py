from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.db.database import get_db
from app.schemas.message import MessageCreate, Message
from app.db.repositories.message import MessageRepository
from app.services.kafka_service import KafkaService
from app.core.dependencies import get_kafka_service
from app.core.exceptions import MessageNotFoundError, DatabaseError
from typing import List
import logging
from app.core.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/messages/",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    responses={
        503: {"description": "Database or Kafka service unavailable"}
    }
)
async def create_message(
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    kafka_service: KafkaService = Depends(get_kafka_service),
    current_user: User = Depends(get_current_user)
) -> Message:
    try:
        repository = MessageRepository(db)
        db_message = await repository.create(message, current_user.id)
        
        async def send_to_kafka(msg: Message):
            try:
                await kafka_service.send_message(repository.to_dict(msg))
            except Exception as ex:
                logger.error(f"Failed to send message to Kafka: {ex}")
            finally:
                await kafka_service.stop_producer()
        
        background_tasks.add_task(send_to_kafka, db_message)
        
        return db_message
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


@router.get(
    "/messages/",
    response_model=List[Message],
    responses={
        503: {"description": "Database service unavailable"}
    }
)
async def get_messages(
    db: AsyncSession = Depends(get_db)
) -> List[Message]:
    try:
        repository = MessageRepository(db)
        return await repository.get_all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


@router.get(
    "/messages/{message_id}",
    response_model=Message,
    responses={
        404: {"description": "Message not found"},
        503: {"description": "Database service unavailable"}
    }
)
async def get_message(
    message_id: int,
    db: AsyncSession = Depends(get_db)
) -> Message:
    try:
        repository = MessageRepository(db)
        message = await repository.get_by_id(message_id)
        if message is None:
            raise MessageNotFoundError(message_id)
        return message
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))
