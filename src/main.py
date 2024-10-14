from fastapi import FastAPI

from src.auth.router import auth_router

app = FastAPI(title="Learnit Backend API routes", docs_url="/")

app.include_router(auth_router, prefix="/api/v1", tags=["User Authentication routes"])
