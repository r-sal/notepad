import asyncio
import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.folders import router as folders_router
from app.api.notes import router as notes_router
from app.core.config import settings
from app.core.scheduler import purge_expired_trash

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Skip scheduler in test mode
    if not os.environ.get("TESTING"):
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            purge_expired_trash,
            "interval",
            hours=6,
            id="purge_expired_trash",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Trash cleanup scheduler started (every 6 hours)")

    yield

    if not os.environ.get("TESTING"):
        scheduler.shutdown(wait=False)
        logger.info("Trash cleanup scheduler stopped")


app = FastAPI(title="Notepad API", version="0.1.0", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(folders_router)
app.include_router(notes_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
