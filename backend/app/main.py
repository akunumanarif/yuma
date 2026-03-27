import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import jobs, stream
from app.services.job_store import job_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def _cleanup_loop():
    while True:
        await asyncio.sleep(3600)  # every hour
        try:
            await job_store.cleanup_old_jobs()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(_cleanup_loop())
    logger.info("Yuma backend started")
    yield
    cleanup_task.cancel()
    logger.info("Yuma backend shutting down")


app = FastAPI(
    title="Yuma API",
    description="AI Timelapse Video Generator",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(stream.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
