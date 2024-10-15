from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.database import get_db
from src.auth import service
from src.auth.schemas import UserAuth
from src.models import User

auth_router = APIRouter()

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_auth: UserAuth, db: AsyncSession=Depends(get_db)):
    """Handles registration of users
    Args:
        user_auth: Schema containing user registration data
    Returns:
        Dict containing info of the newly created user
    """
    try:
        user = await service.create_user(user_auth, db)

        response = {
                "email": user.email,
                "created_at": str(user.created_at)
                }
        headers = {
                "Location": f"/api/v1/users/{user.id}"
                }
        return JSONResponse(content=response, headers=headers, status_code=201)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occured while registering users"
                )

@auth_router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession=Depends(get_db)):
    """Handles login in of users
    Args:
        form_data: From containing user login data
    Returns:
        Dict containing info of the logged in user
    """
    try:
        user = await service.login_user(form_data, db)

        return JSONResponse(content=user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occured while loggin in the user"
                )

@auth_router.get("/users/me", status_code=status.HTTP_200_OK)
async def get_current_user(current_user: Annotated[User, Depends(service.get_current_user)]):
    return current_user
