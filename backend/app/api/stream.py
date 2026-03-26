import asyncio
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.job import JobStatus
from app.services.job_store import job_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["stream"])


@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str):
    queue = await job_store.subscribe(job_id)
    if queue is None:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_generator():
        terminal_statuses = {JobStatus.COMPLETED, JobStatus.FAILED}
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15)
                yield f"data: {event.model_dump_json()}\n\n"
                if event.status in terminal_statuses:
                    break
            except asyncio.TimeoutError:
                yield ": ping\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
