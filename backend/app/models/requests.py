from pydantic import BaseModel, Field
from .job import JobStatus, Job


class CreateJobRequest(BaseModel):
    goal: str = Field(..., min_length=10, max_length=500)
    category: str = Field(..., min_length=1)
    num_stages: int = Field(default=6, ge=4, le=8)


class CreateJobResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    job: Job
