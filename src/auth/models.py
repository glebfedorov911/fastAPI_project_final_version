from typing import TYPE_CHECKING

from fastapi import Depends
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase, SQLAlchemyBaseAccessTokenTableUUID
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from sqlalchemy import String, ForeignKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base, get_async_session

class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"
    __table_args__ = (
        {"extend_existing":True},
    )

    if TYPE_CHECKING:
        username: str
    else:
        username: Mapped[str] = mapped_column(String(length=64), unique=True, nullable=False)

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_access_token_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)

def get_database_strategy(
        access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=60*60*24)