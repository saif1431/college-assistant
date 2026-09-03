from fastapi import APIRouter

from app.api.v1 import chat, health, session

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(session.router, tags=["sessions"])
api_router.include_router(chat.router, tags=["chat"])
