import asyncio
import logging
from pathlib import Path

from app.config import settings
from app.models.job import Job, JobStatus, ProgressEvent, StageStatus, VideoClip
from app.services import image_gen, video_gen, video_stitch, planner as planner_svc
from app.services.job_store import job_store
from app.utils.file_manager import ensure_job_dirs, get_frame_path, get_clip_path, get_output_path
from app.utils.retry import RetryExhausted

logger = logging.getLogger(__name__)

# Limit concurrent pipeline executions
_pipeline_semaphore = asyncio.Semaphore(5)


async def _emit(job: Job, message: str, progress: int, stage_index: int = None, error: str = None):
    event = ProgressEvent(
        job_id=job.id,
        status=job.status,
        progress_percent=progress,
        current_stage_index=stage_index,
        message=message,
        completed_keyframe_urls=[
            s.keyframe_url for s in job.stages if s.keyframe_url and s.status == StageStatus.COMPLETED
        ],
        completed_clips=[c.index for c in job.clips if c.status == StageStatus.COMPLETED],
        output_video_url=job.output_video_url,
        error=error,
    )
    await job_store.emit_progress(job.id, event)
    await job_store.update_job(job)


async def execute_pipeline(job_id: str):
    async with _pipeline_semaphore:
        job = await job_store.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        try:
            await _run_pipeline(job)
        except Exception as e:
            logger.exception(f"Unexpected error in pipeline for job {job_id}: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            await _emit(job, f"Pipeline error: {e}", job.progress_percent, error=str(e))


async def _run_pipeline(job: Job):
    ensure_job_dirs(job.id)

    # ── Phase 1: PLANNING ──────────────────────────────────────────────────────
    job.status = JobStatus.PLANNING
    await _emit(job, "Planning your timelapse scene...", 5)

    try:
        stages = await planner_svc.plan_scene(job.goal, job.category, job.num_stages)
        job.stages = stages
        job.num_stages = len(stages)
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = f"Planning failed: {e}"
        await _emit(job, job.error_message, 5, error=job.error_message)
        return

    await _emit(job, f"Scene planned: {len(job.stages)} stages", 10)

    # ── Phase 2: ANCHOR FRAME (stage 0) ───────────────────────────────────────
    job.status = JobStatus.GENERATING_FRAMES
    num_stages = len(job.stages)
    frame_progress_step = 40 / num_stages

    for i, stage in enumerate(job.stages):
        stage.status = StageStatus.IN_PROGRESS
        progress = int(10 + frame_progress_step * i)
        await _emit(job, f"Generating frame {i + 1}/{num_stages}: {stage.title}", progress, i)

        frame_path = get_frame_path(job.id, i)

        try:
            if i == 0:
                _, fal_url = await image_gen.text_to_image(
                    prompt=stage.prompt,
                    negative_prompt=stage.negative_prompt,
                    local_path=frame_path,
                )
                job.stages[i].fal_cdn_url = fal_url
            else:
                prev_url = job.stages[i - 1].fal_cdn_url
                if not prev_url:
                    raise ValueError(f"No fal URL for previous frame {i - 1}")
                _, fal_url = await image_gen.image_to_image(
                    prompt=stage.prompt,
                    negative_prompt=stage.negative_prompt,
                    source_url=prev_url,
                    local_path=frame_path,
                    strength=stage.img2img_strength,
                )
                job.stages[i].fal_cdn_url = fal_url
        except RetryExhausted as e:
            stage.status = StageStatus.FAILED
            job.status = JobStatus.FAILED
            job.error_message = f"Frame {i} generation failed: {e}"
            await _emit(job, job.error_message, progress, i, error=job.error_message)
            return

        stage.keyframe_local_path = str(frame_path)
        # Use local path as URL for now; can be replaced with CDN URL
        stage.keyframe_url = f"/api/jobs/{job.id}/frames/{i}"
        stage.status = StageStatus.COMPLETED
        progress = int(10 + frame_progress_step * (i + 1))
        await _emit(job, f"Frame {i + 1}/{num_stages} ready", progress, i)

    # ── Phase 3: VIDEO CLIPS (parallel) ───────────────────────────────────────
    job.status = JobStatus.GENERATING_CLIPS
    num_clips = num_stages - 1
    clip_progress_step = 35 / max(num_clips, 1)

    job.clips = [VideoClip(index=i) for i in range(num_clips)]
    await _emit(job, f"Generating {num_clips} video clips in parallel...", 50)

    async def _generate_clip(i: int):
        clip = job.clips[i]
        clip.status = StageStatus.IN_PROGRESS
        start_path = get_frame_path(job.id, i)
        end_path = get_frame_path(job.id, i + 1)
        clip_path = get_clip_path(job.id, i, i + 1)

        try:
            await video_gen.generate_clip(
                start_path=start_path,
                end_path=end_path,
                local_path=clip_path,
                duration=settings.clip_duration_seconds,
            )
            clip.local_path = str(clip_path)
            clip.status = StageStatus.COMPLETED
        except RetryExhausted as e:
            clip.status = StageStatus.FAILED
            raise e

    try:
        await asyncio.gather(*[_generate_clip(i) for i in range(num_clips)])
    except RetryExhausted as e:
        job.status = JobStatus.FAILED
        job.error_message = f"Clip generation failed: {e}"
        await _emit(job, job.error_message, 50, error=job.error_message)
        return

    progress = 85
    await _emit(job, "All clips generated, stitching...", progress)

    # ── Phase 4: STITCH ───────────────────────────────────────────────────────
    job.status = JobStatus.STITCHING
    output_path = get_output_path(job.id)
    clip_paths = [Path(c.local_path) for c in job.clips if c.local_path]

    try:
        await video_stitch.stitch_clips(clip_paths, output_path)
    except video_stitch.FFmpegError as e:
        job.status = JobStatus.FAILED
        job.error_message = f"Stitching failed: {e}"
        await _emit(job, job.error_message, 95, error=job.error_message)
        return

    job.output_video_path = str(output_path)
    job.output_video_url = f"/api/jobs/{job.id}/video"
    job.status = JobStatus.COMPLETED
    job.progress_percent = 100
    await _emit(job, "Timelapse video ready!", 100)
    logger.info(f"Job {job.id} completed successfully")
