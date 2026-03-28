import logging
from pathlib import Path

import fal_client
import httpx

from app.config import settings
from app.utils.retry import retry

logger = logging.getLogger(__name__)


async def _download_file(url: str, local_path: Path) -> Path:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.get(url)
        response.raise_for_status()
        local_path.write_bytes(response.content)
    logger.info(f"Downloaded video {url} → {local_path}")
    return local_path


@retry(max_attempts=3, backoff_base=3.0, retryable_exceptions=(Exception,))
async def generate_clip(
    start_path: Path,
    end_path: Path,
    local_path: Path,
    prompt: str,
    duration: int = None,
) -> Path:
    if duration is None:
        duration = settings.clip_duration_seconds

    logger.info(f"generate_clip: {start_path.name} → {end_path.name}")

    start_url = await fal_client.upload_file_async(str(start_path))

    handler = await fal_client.submit_async(
        "fal-ai/kling-video/v2.1/master/image-to-video",
        arguments={
            "prompt": prompt,
            "image_url": start_url,
            "duration": int(duration),
            "aspect_ratio": settings.kling_aspect_ratio,
            "cfg_scale": 0.5,
        },
    )
    result = await handler.get()
    video_url = result["video"]["url"]
    return await _download_file(video_url, local_path)
