from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import os
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC
from sqlalchemy.exc import StatementError

from .schemas import UserAuth
from src.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def create_user(user: UserAuth, db: AsyncSession) -> User:
    """Creates a user in the database
    Args:
        user: Schema containing the user's creation data
        db: The database session
    Returns:
        The newly created user
    """
    try:
        hashed_password = pwd_context.hash(user.password)
        user = User(
                email=user.email,
                password=hashed_password,
                created_at=datetime.now(UTC)
                )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user
    except StatementError as e:
        await db.rollback()
        raise e
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal server error occured while creating the user")
