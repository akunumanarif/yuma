import json
import logging
import re
from anthropic import AsyncAnthropic

from app.config import settings
from app.models.job import SceneStage

logger = logging.getLogger(__name__)

client = AsyncAnthropic(api_key=settings.anthropic_api_key, timeout=120.0)

SYSTEM_PROMPT = """You are a visual scene planner for AI timelapse videos.
Given a transformation goal, you produce a series of keyframe descriptions
that show a smooth, realistic progression. Each stage should be visually
distinct from the previous, with ~15-20% transformation per step.

CRITICAL RULES for image prompts:
- Always include: lighting conditions, camera angle, time of day
- Maintain consistent: room/environment layout, camera position, art style
- Be specific about what HAS changed vs what stays the same
- Use photorealistic style descriptors consistently across all stages
- Include negative prompts to prevent style drift
- Write prompts in English only"""


async def plan_scene(goal: str, category: str, num_stages: int) -> list[SceneStage]:
    user_message = f"""Create {num_stages} keyframe descriptions for this timelapse:
Goal: {goal}
Category: {category}

Return ONLY a valid JSON array (no markdown, no explanation) with this exact structure:
[
  {{
    "index": 0,
    "title": "Stage name (3-5 words)",
    "description": "What the viewer sees (1-2 sentences)",
    "prompt": "Detailed FLUX image generation prompt (50-100 words). Must include: photorealistic photography, consistent camera angle, lighting conditions.",
    "negative_prompt": "blurry, cartoon, anime, painting, different room, different angle, inconsistent lighting",
    "img2img_strength": 0.70
  }}
]

Stage 0 = starting state (e.g., most messy/unbuilt).
Stage {num_stages - 1} = final state (e.g., fully clean/built).
Intermediate stages show smooth incremental progress.
Keep camera angle and scene layout IDENTICAL across all stages."""

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text.strip()
    json_data = _extract_json(raw_text)
    stages = [SceneStage(**s) for s in json_data]
    logger.info(f"Planned {len(stages)} stages for goal: {goal[:50]}")
    return stages


def _extract_json(text: str) -> list:
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract JSON array from markdown code block or surrounding text
    match = re.search(r'\[[\s\S]*\]', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from planner response: {text[:200]}")
