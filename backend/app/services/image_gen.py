import asyncio
import logging
import httpx
from pathlib import Path

import fal_client

from app.config import settings
from app.utils.retry import retry

logger = logging.getLogger(__name__)


async def _download_file(url: str, local_path: Path) -> Path:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.get(url)
        response.raise_for_status()
        local_path.write_bytes(response.content)
    logger.info(f"Downloaded {url} → {local_path}")
    return local_path


@retry(max_attempts=3, backoff_base=2.0, retryable_exceptions=(Exception,))
async def generate_frame(prompt: str, local_path: Path) -> Path:
    """Text-to-image for all frames using fal-ai/flux/schnell (fast & cheap)."""
    logger.info(f"generate_frame: {prompt[:60]}...")
    handler = await fal_client.submit_async(
        "fal-ai/flux/schnell",
        arguments={
            "prompt": prompt,
            "image_size": settings.flux_image_size,
            "num_inference_steps": 4,
            "num_images": 1,
            "enable_safety_checker": False,
        },
    )
    result = await handler.get()
    image_url = result["images"][0]["url"]
    return await _download_file(image_url, local_path)


async def generate_all_frames(prompts: list[tuple[int, str]], job_id: str) -> dict[int, Path]:
    """Generate all frames in parallel."""
    from app.utils.file_manager import get_frame_path

    async def _gen(index: int, prompt: str) -> tuple[int, Path]:
        path = await generate_frame(prompt, get_frame_path(job_id, index))
        return index, path

    results = await asyncio.gather(*[_gen(i, p) for i, p in prompts])
    return dict(results)
