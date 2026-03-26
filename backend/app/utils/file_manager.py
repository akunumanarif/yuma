from pathlib import Path
from app.config import settings


def get_job_dir(job_id: str) -> Path:
    return Path(settings.temp_dir) / job_id


def get_frame_path(job_id: str, index: int) -> Path:
    return get_job_dir(job_id) / "frames" / f"frame_{index}.png"


def get_clip_path(job_id: str, start: int, end: int) -> Path:
    return get_job_dir(job_id) / "clips" / f"clip_{start}_{end}.mp4"


def get_output_path(job_id: str) -> Path:
    return get_job_dir(job_id) / "output.mp4"


def ensure_job_dirs(job_id: str) -> None:
    for subdir in ["frames", "clips"]:
        (get_job_dir(job_id) / subdir).mkdir(parents=True, exist_ok=True)


def cleanup_job_dir(job_id: str) -> None:
    import shutil
    job_dir = get_job_dir(job_id)
    if job_dir.exists():
        shutil.rmtree(job_dir)
