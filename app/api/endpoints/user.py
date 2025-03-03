from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.db.database import get_db
from app.schemas.user import UserCreate, User
from app.db.repositories.user import UserRepository
from app.core.exceptions import DatabaseError, UserNotFoundError, UserAlreadyExistsError
from typing import List

router = APIRouter()


@router.post(
    "/users/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "User already exists"},
        503: {"description": "Database error"}
    }
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        repository = UserRepository(db)
        return await repository.create(user)
    except IntegrityError:
        raise UserAlreadyExistsError()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


@router.get(
    "/users/",
    response_model=List[User],
    responses={
        503: {"description": "Database error"}
    }
)
async def get_users(
    db: AsyncSession = Depends(get_db)
) -> List[User]:
    try:
        repository = UserRepository(db)
        return await repository.get_all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


@router.get(
    "/users/{user_id}",
    response_model=User,
    responses={
        404: {"description": "User not found"},
        503: {"description": "Database error"}
    }
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        repository = UserRepository(db)
        user = await repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "User not found"},
        503: {"description": "Database error"}
    }
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = UserRepository(db)
        if not await repository.delete(user_id):
            raise UserNotFoundError(user_id)
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))
