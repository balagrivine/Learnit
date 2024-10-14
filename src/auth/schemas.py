from pydantic import BaseModel, Field, EmailStr

class UserAuth(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6, max_length=128, description="Password is required")

    class Config:
        json_schema_extra = {
                "example": {
                    "email": "example@gmail.com",
                    "password": "Str@ngpass254!."
                }
        }
