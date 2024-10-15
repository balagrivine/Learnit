from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import os
from typing import Dict, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC, timedelta
from sqlalchemy import select
from sqlalchemy.exc import StatementError

from .schemas import UserAuth
from src.models import User
from src.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")

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

async def login_user(form_data, db: AsyncSession) -> Dict[any, str]:
    try:
        user = await get_user(form_data.username, db)

        if not user or not pwd_context.verify(form_data.password, user.password):
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW_Authenticate":"Bearer"}
                    )
        access_token = create_access_token(data={"sub": user.email})
        return {
                "user_id": user.id,
                "email": user.email,
                "token_type": "bearer",
                "access_token": access_token
                }
    except Exception as e:
        raise e

async def get_user(email: str, db: AsyncSession) -> User:
    stmt = select(User).where(User.email==email)
    result = await db.execute(stmt)
    return result.scalar()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(hours=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession=Depends(get_db)):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate":"Bearer"},
            )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload["sub"]
        if email is None:
            raise credentials_exception

        user = await get_user(email, db)
        if not user:
            raise credentials_exception
        return user
    except InvalidTokenError:
        raise credentials_exception
