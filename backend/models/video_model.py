import torch
import asyncio
from typing import Optional, List, Tuple
from PIL import Image
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

from diffusers import StableVideoDiffusionPipeline
from ..core.config import get_settings
from ..core.device import DeviceManager
from ..core.exceptions import ModelLoadError, GenerationError
from .base import BaseModelManager


class VideoModelManager(BaseModelManager):
    def __init__(self, hf_token: Optional[str] = None):
        super().__init__(hf_token)
        self.settings = get_settings()
        self.repo_id = "stabilityai/stable-video-diffusion-img2vid-xt"
        self.dtype = DeviceManager.get_dtype(self.device, True)
    
    async def ensure_loaded(self) -> None:
        async with self._lock:
            if self.pipe is not None:
                return
            
            self.logger.info(f"Loading video model {self.repo_id}")
            loop = asyncio.get_running_loop()
            
            try:
                self.pipe = await loop.run_in_executor(None, self._load_pipeline)
            except Exception as e:
                raise ModelLoadError(f"Failed to load video model: {e}")
    
    def _load_pipeline(self) -> StableVideoDiffusionPipeline:
        pipe = StableVideoDiffusionPipeline.from_pretrained(
            self.repo_id,
            torch_dtype=self.dtype,
            use_safetensors=True,
            token=self.hf_token,
            cache_dir=self.settings.hf_home,
        )
        
        try:
            pipe.enable_vae_slicing()
            pipe.enable_attention_slicing("max")
        except Exception:
            pass
        
        return pipe.to(self.device)
    
    def _resize_for_model(self, width: int, height: int, max_short: int = 576) -> Tuple[int, int]:
        if min(width, height) > max_short:
            scale = max_short / min(width, height)
            width = int(width * scale)
            height = int(height * scale)
        
        width = max(256, (width // 8) * 8)
        height = max(256, (height // 8) * 8)
        
        return width, height
    
    def _create_seamless_loop(self, frames: List[Image.Image]) -> List[Image.Image]:
        if len(frames) < 2:
            return frames
        return frames + frames[-2:0:-1]
    
    def _enhance_frames(self, frames: List[Image.Image]) -> List[Image.Image]:
        if not HAS_CV2:
            return frames
        
        enhanced = []
        for frame in frames:
            arr = np.array(frame)
            arr = cv2.bilateralFilter(arr, 5, 40, 40)
            blur = cv2.GaussianBlur(arr, (0, 0), sigmaX=1.0)
            sharp = cv2.addWeighted(arr, 1.15, blur, -0.15, 0)
            enhanced.append(Image.fromarray(sharp))
        
        return enhanced
    
    async def img2vid_clip(
        self,
        base_image: Image.Image,
        num_frames: int = 24,
        fps: int = 24,
        motion_bucket_id: int = 96,
        noise_aug_strength: float = 0.02,
        seed: Optional[int] = None,
        enhance_quality: bool = True,
    ) -> Tuple[List[Image.Image], int, int]:
        await self.ensure_loaded()
        
        width, height = base_image.size
        new_w, new_h = self._resize_for_model(width, height)
        if (width, height) != (new_w, new_h):
            image = base_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            image = base_image
        
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        
        loop = asyncio.get_running_loop()
        
        try:
            with torch.inference_mode():
                result = await loop.run_in_executor(
                    None,
                    lambda: self.pipe(
                        image=image,
                        num_frames=num_frames,
                        decode_chunk_size=8,
                        motion_bucket_id=motion_bucket_id,
                        noise_aug_strength=noise_aug_strength,
                        fps=fps,
                        width=image.width,
                        height=image.height,
                        generator=generator,
                    )
                )
            
            frames = result.frames[0]
            
            if enhance_quality:
                frames = self._enhance_frames(frames)
            
            frames = self._create_seamless_loop(frames)
            
            return frames, image.width, image.height
            
        except Exception as e:
            raise GenerationError(f"Video generation failed: {e}")

    async def infer(self, **kwargs):
        return await self.img2vid_clip(**kwargs)