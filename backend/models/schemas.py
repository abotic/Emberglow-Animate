from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class ArtStyle(str, Enum):
    CINEMATIC = "Cinematic"
    PHOTOGRAPHIC = "Photographic"
    ANIME = "Anime"
    FANTASY = "Fantasy Art"
    DIGITAL = "Digital Art"
    MODEL_3D = "3D Model"
    NEON_PUNK = "Neon Punk"
    OIL_PAINTING = "Oil Painting"
    WATERCOLOR = "Watercolor"
    FREESTYLE = "Freestyle"


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    style: ArtStyle = ArtStyle.CINEMATIC
    num_inference_steps: int = Field(44, ge=1, le=150)
    guidance_scale: float = Field(7.5, ge=0.0, le=20.0)
    width: int = Field(1024, ge=256, le=2048)
    height: int = Field(1024, ge=256, le=2048)
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

    @validator("width", "height")
    def validate_dimensions(cls, v):
        if v % 8 != 0:
            raise ValueError("Dimensions must be divisible by 8")
        return v


class BatchImageRequest(BaseModel):
    items: List[ImageGenerationRequest] = Field(..., min_items=1, max_items=10000)
    save_to_disk: bool = False
    prefix: Optional[str] = None
    start_seed: Optional[int] = None
    micro_batch_size: int = Field(4, ge=1, le=64)


class VideoGenerationOptions(BaseModel):
    duration_minutes: float = Field(30.0, ge=0.1, le=240.0)
    fps: int = Field(24, ge=8, le=30)
    motion: int = Field(96, ge=0, le=255)
    preserve_strength: float = Field(0.02, ge=0.0, le=1.0)
    num_frames: int = Field(24, ge=14, le=25)
    enhance_quality: bool = True
    seed: Optional[int] = 1234