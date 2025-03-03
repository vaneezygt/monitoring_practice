from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.message import Message
from app.schemas.message import MessageCreate
from typing import List, Optional, Dict, Any


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message: MessageCreate, user_id: int) -> Message:
        db_message = Message(**message.model_dump(), user_id=user_id)
        self.session.add(db_message)
        await self.session.commit()
        await self.session.refresh(db_message)
        return db_message

    async def get_by_id(self, message_id: int) -> Optional[Message]:
        stmt = (
            select(Message)
            .options(selectinload(Message.user))
            .where(Message.id == message_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Message]:
        stmt = select(Message).options(selectinload(Message.user))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def to_dict(message: Message) -> Dict[str, Any]:
        """Convert message model to dictionary for Kafka"""
        return {
            "id": message.id,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "user_id": message.user_id
        }
