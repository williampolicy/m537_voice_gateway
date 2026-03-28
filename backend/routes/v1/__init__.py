"""
M537 Voice Gateway - API v1 Routes
"""
from fastapi import APIRouter

from .voice import router as voice_router
from .health import router as health_router

router = APIRouter(prefix="/v1")

router.include_router(voice_router, tags=["voice-v1"])
router.include_router(health_router, tags=["health-v1"])
