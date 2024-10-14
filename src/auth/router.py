from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.auth import service
from src.auth.schemas import UserAuth

auth_router = APIRouter()

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_auth: UserAuth, db: AsyncSession=Depends(get_db)):
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
        raise e
