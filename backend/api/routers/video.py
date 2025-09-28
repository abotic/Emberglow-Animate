import asyncio
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import os

from ...models.schemas import VideoGenerationOptions
from ...models.video_model import VideoModelManager
from ...services.job_service import job_service, JobStatus
from ...services.video_processor import VideoProcessor
from ...core.config import get_settings
from ..dependencies import require_api_key

router = APIRouter(prefix="/api/video", tags=["video"])

class VideoGenerator:
    def __init__(self):
        settings = get_settings()
        self._manager = VideoModelManager(hf_token=settings.hf_token)
        self._processor = VideoProcessor(settings.output_dir, settings.temp_dir)
    
    async def generate_async(
        self,
        file_content: bytes,
        options: VideoGenerationOptions
    ) -> str:
        job_id = job_service.create_job(options.dict())
        asyncio.create_task(self._process_video(job_id, file_content, options))
        return job_id
    
    async def _process_video(
        self,
        job_id: str,
        file_content: bytes,
        options: VideoGenerationOptions
    ):
        try:
            job_service.update_job(job_id, status=JobStatus.LOADING)
            base_image = self._processor.load_image(file_content)
            
            job_service.update_job(job_id, status=JobStatus.GENERATING)
            frames, width, height = await self._manager.img2vid_clip(
                base_image=base_image,
                num_frames=options.num_frames,
                fps=options.fps,
                motion_bucket_id=options.motion,
                noise_aug_strength=options.preserve_strength,
                seed=options.seed,
                enhance_quality=options.enhance_quality,
            )
            
            job_service.update_job(job_id, status=JobStatus.ENCODING)
            output_path = await self._processor.create_looped_video(
                frames=frames,
                fps=options.fps,
                duration_minutes=options.duration_minutes,
                job_id=job_id
            )
            
            job_service.update_job(
                job_id,
                status=JobStatus.DONE,
                progress=1.0,
                result={
                    "video_path": output_path,
                    "width": width,
                    "height": height,
                    "fps": options.fps,
                    "duration_minutes": options.duration_minutes,
                }
            )
        except Exception as e:
            job_service.update_job(
                job_id,
                status=JobStatus.ERROR,
                error=str(e)
            )

generator = VideoGenerator()

@router.post("/generate_loop_from_upload", dependencies=[Depends(require_api_key)])
async def generate_video(
    file: UploadFile = File(...),
    duration_minutes: float = Query(30.0, ge=0.1, le=240.0),
    fps: int = Query(24, ge=8, le=30),
    motion: int = Query(96, ge=0, le=255),
    preserve_strength: float = Query(0.02, ge=0.0, le=1.0),
    num_frames: int = Query(24, ge=14, le=25),
    enhance_quality: bool = Query(True),
    seed: Optional[int] = Query(1234),
):
    options = VideoGenerationOptions(
        duration_minutes=duration_minutes,
        fps=fps,
        motion=motion,
        preserve_strength=preserve_strength,
        num_frames=num_frames,
        enhance_quality=enhance_quality,
        seed=seed,
    )
    
    content = await file.read()
    job_id = await generator.generate_async(content, options)
    
    return JSONResponse(
        status_code=202,
        content={
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "status_url": f"/api/video/job/{job_id}",
            "poll_interval_s": 2,
        },
    )

@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "error": job.get("error"),
    }
    
    if job["status"] == JobStatus.DONE and job.get("result"):
        result = job["result"]
        filename = os.path.basename(result["video_path"])
        response.update({
            "video_url": f"/files/{filename}",
            "fps": result["fps"],
            "duration_minutes": result["duration_minutes"],
            "width": result["width"],
            "height": result["height"],
        })
    
    return JSONResponse(
        content=response,
        headers={"Cache-Control": "no-store"}
    )

@router.post("/warmup")
async def warmup():
    await generator._manager.ensure_loaded()
    return {"ok": True}