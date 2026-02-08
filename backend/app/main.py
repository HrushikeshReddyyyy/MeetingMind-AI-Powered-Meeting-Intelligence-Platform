"""
MeetingMind API - AI-Powered Meeting Intelligence Platform

Main FastAPI application entry point. Configures routes, middleware,
database initialization, and serves the API documentation.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import meetings, action_items, integrations, analytics

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    logger.info("Starting MeetingMind API...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down MeetingMind API...")


app = FastAPI(
    title="MeetingMind API",
    description="AI-Powered Meeting Intelligence Platform - Automates meeting documentation through "
                "AI-powered transcription, smart summaries, and action item tracking.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
origins = [origin.strip() for origin in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(meetings.router)
app.include_router(action_items.router)
app.include_router(integrations.router)
app.include_router(analytics.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MeetingMind API",
        "version": "1.0.0",
    }
