from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime
import uuid

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    SCRIPTING = "SCRIPTING"
    VISUALIZING = "VISUALIZING"
    VOICING = "VOICING"
    EDITING = "EDITING"
    READY_TO_POST = "READY_TO_POST"
    POSTING = "POSTING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"

class DurationMode(str, Enum):
    """Video duration options"""
    AUTO = "auto"           # Based on script narration length
    QUICK = "quick_15s"     # ~15 seconds
    SHORT = "short_30s"     # ~30 seconds
    MEDIUM = "medium_60s"   # ~60 seconds
    LONG = "long_90s"       # ~90 seconds

class Scene(BaseModel):
    narration: str
    visual_prompt: str
    visual_text: Optional[str] = None
    estimated_duration: float = 5.0
    image_path: Optional[str] = None
    audio_path: Optional[str] = None

class JobCreate(BaseModel):
    topic: str
    tone: str = "Futuristic, Curious"
    scene_count: int = 4
    image_style: str = "Cinematic"
    duration_mode: DurationMode = DurationMode.AUTO  # Default: based on script

class Job(BaseModel):
    id: str
    topic: str
    status: TaskStatus
    created_at: datetime
    # New fields
    scene_count: int = 4
    image_style: str = "Cinematic"
    duration_mode: DurationMode = DurationMode.AUTO
    
    script: Optional[List[Scene]] = None
    caption: Optional[str] = None
    video_path: Optional[str] = None
    error_msg: Optional[str] = None
    logs: List[str] = []

class JobDB:
    # Simulating a DB for now
    jobs: dict = {}

    @staticmethod
    def get(job_id: str) -> Optional[Job]:
        return JobDB.jobs.get(job_id)

    @staticmethod
    def create(job_req: JobCreate) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            topic=job_req.topic,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            scene_count=job_req.scene_count,
            image_style=job_req.image_style,
            duration_mode=job_req.duration_mode,
            logs=["Job created."]
        )
        JobDB.jobs[job_id] = job
        return job

    @staticmethod
    def add_log(job_id: str, message: str):
        if job_id in JobDB.jobs:
            job = JobDB.jobs[job_id]
            timestamp = datetime.now().strftime("%H:%M:%S")
            job.logs.append(f"[{timestamp}] {message}")
            JobDB.jobs[job_id] = job # Not strictly necessary for mutable obj but good practice

    @staticmethod
    def update(job_id: str, **kwargs):
        if job_id in JobDB.jobs:
            job_data = JobDB.jobs[job_id].model_dump()
            job_data.update(kwargs)
            JobDB.jobs[job_id] = Job(**job_data)
