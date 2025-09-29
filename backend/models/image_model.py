import torch
import asyncio
from typing import Optional
from PIL import Image
from diffusers import DiffusionPipeline
from ..core.config import get_settings
from ..core.device import DeviceManager
from ..core.exceptions import ModelLoadError, GenerationError
from .base import BaseModelManager

class ImageModelManager(BaseModelManager):
    def __init__(self, hf_token: Optional[str] = None):
        super().__init__(hf_token)
        self.settings = get_settings()
        self.repo_id = "stabilityai/stable-diffusion-3.5-large"
        self.dtype = DeviceManager.get_dtype(self.device, self.settings.force_fp16)
        self.variant = "fp16" if self.device == "cuda" else None
    
    def _configure_pipeline(self, pipe: DiffusionPipeline) -> DiffusionPipeline:
        """Configure pipeline optimizations"""
        try:
            if hasattr(pipe, "enable_vae_slicing"):
                pipe.enable_vae_slicing()
            if hasattr(pipe, "enable_vae_tiling"):
                pipe.enable_vae_tiling()
        except Exception as e:
            self.logger.warning(f"Failed to enable VAE optimizations: {e}")
        return pipe
    
    async def ensure_loaded(self) -> None:
        # This function already has a lock for loading, which is great.
        async with self._lock:
            if self.pipe is not None:
                return
            
            self.logger.info(f"Loading model {self.repo_id}")
            loop = asyncio.get_running_loop()
            
            try:
                self.pipe = await loop.run_in_executor(
                    None,
                    lambda: self._load_pipeline()
                )
            except Exception as e:
                raise ModelLoadError(f"Failed to load image model: {e}")
    
    def _load_pipeline(self) -> DiffusionPipeline:
        pipe = DiffusionPipeline.from_pretrained(
            self.repo_id,
            torch_dtype=self.dtype,
            use_safetensors=True,
            token=self.hf_token,
            cache_dir=self.settings.hf_home,
            variant=self.variant,
        )
        pipe = self._configure_pipeline(pipe)
        return pipe.to(self.device)
    
    async def infer(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 44,
        guidance_scale: float = 7.5,
        width: int = 1024,
        height: int = 1024,
        seed: Optional[int] = None,
    ) -> Image.Image:
        # This lock ensures only one thread can execute the generation code at a time.
        async with self._lock:
            await self.ensure_loaded()
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            
            loop = asyncio.get_running_loop()
            
            try:
                with torch.inference_mode():
                    result = await loop.run_in_executor(
                        None,
                        lambda: self.pipe(
                            prompt=prompt,
                            negative_prompt=negative_prompt,
                            num_inference_steps=num_inference_steps,
                            guidance_scale=guidance_scale,
                            width=width,
                            height=height,
                            generator=generator,
                        )
                    )
                return result.images[0]
            except Exception as e:
                raise GenerationError(f"Image generation failed: {e}")