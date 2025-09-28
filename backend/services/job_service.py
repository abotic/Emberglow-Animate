from typing import Dict, Optional, Any
from enum import Enum
import uuid
import time
from ..core.logging import get_logger

class JobStatus(str, Enum):
    QUEUED = "queued"
    LOADING = "loading"
    GENERATING = "generating"
    ENCODING = "encoding"
    DONE = "done"
    ERROR = "error"

class JobService:
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger(__name__)
    
    def create_job(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        job_id = uuid.uuid4().hex
        self._jobs[job_id] = {
            "id": job_id,
            "status": JobStatus.QUEUED,
            "progress": 0.0,
            "error": None,
            "result": None,
            "created_at": time.time(),
            "metadata": metadata or {},
        }
        self.logger.info(f"Created job {job_id}")
        return job_id
    
    def update_job(self, job_id: str, **updates) -> None:
        if job_id in self._jobs:
            self._jobs[job_id].update(updates)
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)
    
    def cleanup_old_jobs(self, max_age_seconds: int = 3600) -> None:
        current_time = time.time()
        to_remove = [
            job_id for job_id, job in self._jobs.items()
            if current_time - job["created_at"] > max_age_seconds
        ]
        for job_id in to_remove:
            del self._jobs[job_id]
        if to_remove:
            self.logger.info(f"Cleaned up {len(to_remove)} old jobs")

job_service = JobService()