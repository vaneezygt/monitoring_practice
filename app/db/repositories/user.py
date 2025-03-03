from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from typing import List, Optional


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserCreate) -> User:
        user_data = user.model_dump(exclude={'password'})
        user_data['hashed_password'] = get_password_hash(user.password)
        
        db_user = User(**user_data)
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[User]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        db_user = await self.get_by_id(user_id)
        if db_user:
            for key, value in user_data.items():
                setattr(db_user, key, value)
            await self.session.commit()
            await self.session.refresh(db_user)
        return db_user

    async def delete(self, user_id: int) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return bool(result.rowcount())
