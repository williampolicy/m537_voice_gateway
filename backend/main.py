"""
M537 Voice Gateway - Main Application Entry
LIGHT HOPE Voice Gateway for server ecosystem access
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import time
import os

from settings import settings
from routes import voice, health, metrics, monitoring, websocket
from middleware import RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info(f"M537 Voice Gateway starting on port {settings.PORT}")
    logger.info(f"Ecosystem version: LIGHT HOPE {settings.ECOSYSTEM_VERSION}")
    logger.info(f"Projects base path: {settings.PROJECTS_BASE_PATH}")
    yield
    # Shutdown
    logger.info("M537 Voice Gateway shutting down")


app = FastAPI(
    title="M537 Voice Gateway",
    description="LIGHT HOPE Voice Gateway - Unified voice access layer for server ecosystem",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


# Register API routes
app.include_router(voice.router, prefix="/api", tags=["voice"])
app.include_router(health.router, tags=["health"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])
app.include_router(monitoring.router, prefix="/api", tags=["monitoring"])
app.include_router(websocket.router, tags=["websocket"])


# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
