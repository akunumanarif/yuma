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
async def text_to_image(prompt: str, negative_prompt: str, local_path: Path) -> Path:
    logger.info(f"text_to_image: {prompt[:60]}...")
    handler = await fal_client.submit_async(
        "fal-ai/flux/dev",
        arguments={
            "prompt": prompt,
            "image_size": settings.flux_image_size,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "num_images": 1,
            "enable_safety_checker": False,
        },
    )
    result = await handler.get()
    image_url = result["images"][0]["url"]
    return await _download_file(image_url, local_path)


@retry(max_attempts=3, backoff_base=2.0, retryable_exceptions=(Exception,))
async def image_to_image(
    prompt: str,
    negative_prompt: str,
    source_path: Path,
    local_path: Path,
    strength: float = 0.70,
) -> Path:
    logger.info(f"image_to_image (strength={strength}): {prompt[:60]}...")
    # Upload source image to fal CDN
    image_url = await fal_client.upload_file_async(str(source_path))

    handler = await fal_client.submit_async(
        "fal-ai/flux/dev/image-to-image",
        arguments={
            "prompt": prompt,
            "image_url": image_url,
            "strength": strength,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "num_images": 1,
            "enable_safety_checker": False,
        },
    )
    result = await handler.get()
    image_url_out = result["images"][0]["url"]
    return await _download_file(image_url_out, local_path)
