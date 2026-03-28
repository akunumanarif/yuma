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
    """Text-to-image for anchor frame using fal-ai/flux/schnell (fast & cheap)."""
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


@retry(max_attempts=3, backoff_base=2.0, retryable_exceptions=(Exception,))
async def generate_frame_img2img(
    prompt: str,
    reference_path: Path,
    local_path: Path,
    strength: float = 0.65,
) -> Path:
    """img2img using anchor frame as reference for visual consistency."""
    logger.info(f"generate_frame_img2img (strength={strength:.2f}): {prompt[:60]}...")
    reference_url = await fal_client.upload_file_async(str(reference_path))
    handler = await fal_client.submit_async(
        "fal-ai/flux/dev/image-to-image",
        arguments={
            "prompt": prompt,
            "image_url": reference_url,
            "strength": strength,
            "image_size": settings.flux_image_size,
            "num_inference_steps": 28,
            "num_images": 1,
            "enable_safety_checker": False,
        },
    )
    result = await handler.get()
    image_url = result["images"][0]["url"]
    return await _download_file(image_url, local_path)


async def generate_all_frames_with_anchor(
    prompts: list[tuple[int, str]], job_id: str
) -> dict[int, Path]:
    """
    Generate frame 0 via text-to-image (anchor), then all subsequent frames
    via img2img using frame 0 as the reference — remaining frames run in parallel.
    """
    from app.utils.file_manager import get_frame_path

    if not prompts:
        return {}

    sorted_prompts = sorted(prompts, key=lambda x: x[0])
    anchor_index, anchor_prompt = sorted_prompts[0]
    anchor_path = get_frame_path(job_id, anchor_index)

    # Step 1: Generate anchor frame (text-to-image)
    logger.info(f"Generating anchor frame {anchor_index}...")
    await generate_frame(anchor_prompt, anchor_path)

    if len(sorted_prompts) == 1:
        return {anchor_index: anchor_path}

    # Step 2: Generate remaining frames via img2img in parallel, all referencing anchor
    num_remaining = len(sorted_prompts) - 1

    async def _gen_img2img(index: int, prompt: str, position: int) -> tuple[int, Path]:
        strength = min(0.55 + (position / num_remaining) * 0.20, 0.75)
        path = get_frame_path(job_id, index)
        await generate_frame_img2img(prompt, anchor_path, path, strength=strength)
        return index, path

    tasks = [
        _gen_img2img(idx, prompt, pos)
        for pos, (idx, prompt) in enumerate(sorted_prompts[1:], start=1)
    ]
    results = await asyncio.gather(*tasks)

    return {anchor_index: anchor_path, **dict(results)}
