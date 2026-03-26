import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class FFmpegError(Exception):
    pass


async def stitch_clips(clip_paths: list[Path], output_path: Path) -> Path:
    if not clip_paths:
        raise ValueError("No clips to stitch")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write FFmpeg concat list file
    list_file = output_path.with_suffix(".txt")
    with open(list_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-movflags", "+faststart",
        str(output_path),
    ]

    logger.info(f"Stitching {len(clip_paths)} clips → {output_path}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise FFmpegError(f"FFmpeg failed (code {proc.returncode}): {stderr.decode()}")

    # Cleanup list file
    list_file.unlink(missing_ok=True)
    logger.info(f"Stitch complete: {output_path}")
    return output_path
