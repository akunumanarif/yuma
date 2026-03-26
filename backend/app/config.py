from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # AI APIs
    anthropic_api_key: str
    fal_key: str

    # Storage
    temp_dir: str = "./temp/jobs"
    max_job_age_hours: int = 24

    # Server
    cors_origins: str = "http://localhost:3000"

    # Pipeline tuning
    default_num_stages: int = 6
    img2img_strength_default: float = 0.70
    clip_duration_seconds: int = 5
    kling_aspect_ratio: str = "16:9"
    flux_image_size: str = "landscape_16_9"

    # Timeouts / Retries
    fal_poll_timeout_seconds: int = 600
    fal_max_retries: int = 3

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
