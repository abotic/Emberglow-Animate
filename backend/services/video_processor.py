import os
import tempfile
import subprocess
import asyncio
from typing import List
from PIL import Image
import io
from ..core.logging import get_logger


class VideoProcessor:
    def __init__(self, output_dir: str, temp_dir: str):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.logger = get_logger(__name__)
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
    
    def load_image(self, content: bytes) -> Image.Image:
        return Image.open(io.BytesIO(content)).convert("RGB")
    
    async def create_looped_video(
        self,
        frames: List[Image.Image],
        fps: int,
        duration_minutes: float,
        job_id: str
    ) -> str:
        temp_path = os.path.join(self.temp_dir, f"temp_{job_id}.mp4")
        final_path = os.path.join(self.output_dir, f"{job_id}.mp4")
        
        try:
            await self._encode_frames(frames, fps, temp_path)
            await self._loop_video(temp_path, final_path, duration_minutes)
            return final_path
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def _encode_frames(self, frames: List[Image.Image], fps: int, output: str):
        work_dir = tempfile.mkdtemp(prefix="frames_", dir=self.temp_dir)
        try:
            for i, frame in enumerate(frames):
                frame.save(os.path.join(work_dir, f"frame_{i:06d}.png"))
            
            pattern = os.path.join(work_dir, "frame_%06d.png")
            await self._run_ffmpeg([
                "ffmpeg", "-y", "-v", "error",
                "-framerate", str(fps), "-i", pattern,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "18", "-movflags", "+faststart",
                output
            ])
        finally:
            for file in os.listdir(work_dir):
                os.remove(os.path.join(work_dir, file))
            os.rmdir(work_dir)
    
    async def _loop_video(self, input_path: str, output_path: str, duration_minutes: float):
        duration_seconds = int(duration_minutes * 60)
        await self._run_ffmpeg([
            "ffmpeg", "-y", "-v", "error",
            "-stream_loop", "-1", "-i", input_path,
            "-t", str(duration_seconds), "-c", "copy",
            output_path
        ])
    
    async def _run_ffmpeg(self, cmd: List[str]):
        loop = asyncio.get_running_loop()
        proc = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, capture_output=True, text=True)
        )
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {proc.stderr}")