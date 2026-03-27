from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    GENERATING_FRAMES = "generating_frames"
    GENERATING_CLIPS = "generating_clips"
    STITCHING = "stitching"
    COMPLETED = "completed"
    FAILED = "failed"


class StageStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SceneStage(BaseModel):
    index: int
    title: str
    description: str
    prompt: str
    negative_prompt: str = ""
    img2img_strength: float = 0.70
    keyframe_url: Optional[str] = None
    keyframe_local_path: Optional[str] = None
    fal_cdn_url: Optional[str] = None
    status: StageStatus = StageStatus.PENDING


class VideoClip(BaseModel):
    index: int
    local_path: Optional[str] = None
    fal_job_id: Optional[str] = None
    status: StageStatus = StageStatus.PENDING


class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    category: str
    num_stages: int = 6
    status: JobStatus = JobStatus.PENDING
    stages: list[SceneStage] = []
    clips: list[VideoClip] = []
    output_video_path: Optional[str] = None
    output_video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    progress_percent: int = 0


class ProgressEvent(BaseModel):
    job_id: str
    status: JobStatus
    progress_percent: int
    current_stage_index: Optional[int] = None
    message: str
    completed_keyframe_urls: list[str] = []
    completed_clips: list[int] = []
    output_video_url: Optional[str] = None
    error: Optional[str] = None
