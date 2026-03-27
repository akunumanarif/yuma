import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.models.job import Job, JobStatus, ProgressEvent
from app.utils.file_manager import cleanup_job_dir
from app.config import settings

logger = logging.getLogger(__name__)


class JobStore:
    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._queues: dict[str, asyncio.Queue] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def create_job(self, job: Job) -> None:
        async with self._lock:
            self._jobs[job.id] = job
            self._queues[job.id] = asyncio.Queue(maxsize=200)

    def register_task(self, job_id: str, task: asyncio.Task) -> None:
        self._tasks[job_id] = task

    async def get_job(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    async def update_job(self, job: Job) -> None:
        async with self._lock:
            job.updated_at = datetime.utcnow()
            self._jobs[job.id] = job

    async def emit_progress(self, job_id: str, event: ProgressEvent) -> None:
        queue = self._queues.get(job_id)
        if queue:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(f"Progress queue full for job {job_id}, dropping event")

    async def subscribe(self, job_id: str) -> Optional[asyncio.Queue]:
        return self._queues.get(job_id)

    async def cancel_job(self, job_id: str) -> bool:
        task = self._tasks.get(job_id)
        if task and not task.done():
            task.cancel()
        return await self.delete_job(job_id)

    async def delete_job(self, job_id: str) -> bool:
        async with self._lock:
            if job_id not in self._jobs:
                return False
            del self._jobs[job_id]
            if job_id in self._queues:
                del self._queues[job_id]
            if job_id in self._tasks:
                del self._tasks[job_id]
        cleanup_job_dir(job_id)
        return True

    async def cleanup_old_jobs(self) -> None:
        cutoff = datetime.utcnow() - timedelta(hours=settings.max_job_age_hours)
        async with self._lock:
            old_ids = [
                job_id for job_id, job in self._jobs.items()
                if job.created_at < cutoff
            ]
        for job_id in old_ids:
            logger.info(f"Cleaning up old job {job_id}")
            await self.delete_job(job_id)


job_store = JobStore()
