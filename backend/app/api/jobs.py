import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.job import Job, JobStatus
from app.models.requests import CreateJobRequest, CreateJobResponse, JobStatusResponse
from app.services.job_store import job_store
from app.pipeline.executor import execute_pipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=CreateJobResponse, status_code=201)
async def create_job(request: CreateJobRequest):
    job = Job(
        goal=request.goal,
        category=request.category,
        num_stages=request.num_stages,
    )
    await job_store.create_job(job)
    asyncio.create_task(execute_pipeline(job.id))
    logger.info(f"Created job {job.id} for goal: {request.goal[:50]}")
    return CreateJobResponse(job_id=job.id, status=job.status)


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job(job_id: str):
    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(job=job)


@router.get("/{job_id}/video")
async def get_video(job_id: str):
    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.COMPLETED or not job.output_video_path:
        raise HTTPException(status_code=404, detail="Video not ready")

    video_path = Path(job.output_video_path)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=f"timelapse_{job_id}.mp4",
    )


@router.get("/{job_id}/frames/{frame_index}")
async def get_frame(job_id: str, frame_index: int):
    from app.utils.file_manager import get_frame_path
    frame_path = get_frame_path(job_id, frame_index)
    if not frame_path.exists():
        raise HTTPException(status_code=404, detail="Frame not found")
    return FileResponse(path=str(frame_path), media_type="image/png")


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str):
    deleted = await job_store.cancel_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
