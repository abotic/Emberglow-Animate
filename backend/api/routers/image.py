from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import base64
import io
from PIL import Image

from ...models.schemas import ImageGenerationRequest, ArtStyle
from ...core.exceptions import GenerationError
from ..dependencies import require_api_key
from ...core.state import image_manager

router = APIRouter(prefix="/api/image", tags=["image"])

STYLE_PROMPTS = {
    ArtStyle.CINEMATIC: "cinematic lighting, movie still, dramatic atmosphere",
    ArtStyle.PHOTOGRAPHIC: "professional photography, ultra realistic, 8k",
    ArtStyle.ANIME: "anime art style, studio quality, vibrant colors",
    ArtStyle.FANTASY: "fantasy art, magical atmosphere, ethereal lighting",
    ArtStyle.DIGITAL: "digital painting, concept art, highly detailed",
    ArtStyle.MODEL_3D: "3d render, octane render, volumetric lighting",
    ArtStyle.NEON_PUNK: "cyberpunk, neon lights, futuristic",
    ArtStyle.OIL_PAINTING: "oil painting, traditional art, textured brushstrokes",
    ArtStyle.WATERCOLOR: "watercolor painting, soft edges, flowing colors",
    ArtStyle.FREESTYLE: "",
}

DEFAULT_NEGATIVE = "low quality, blurry, distorted, watermark, text, error"

class ImageGenerator:
    def __init__(self):
        self._manager = image_manager
    
    async def generate(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        prompt = self._enhance_prompt(request.prompt, request.style)
        negative = request.negative_prompt or DEFAULT_NEGATIVE
        
        try:
            image = await self._manager.infer(
                prompt=prompt,
                negative_prompt=negative,
                num_inference_steps=min(request.num_inference_steps, 120),
                guidance_scale=request.guidance_scale,
                width=request.width,
                height=request.height,
                seed=request.seed
            )
            
            return self._format_response(image, request)
        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"Generation failed: {e}")
    
    def _enhance_prompt(self, prompt: str, style: ArtStyle) -> str:
        style_prompt = STYLE_PROMPTS.get(style, "")
        if style_prompt:
            return f"{prompt}, {style_prompt}, masterpiece, best quality"
        return prompt
    
    def _format_response(self, image: Image.Image, request: ImageGenerationRequest) -> Dict[str, Any]:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return {
            "success": True,
            "image_url": f"data:image/png;base64,{encoded}",
            "model_used": "sd3",
            "width": request.width,
            "height": request.height,
            "num_inference_steps": request.num_inference_steps,
        }

generator = ImageGenerator()

@router.post("/generate", dependencies=[Depends(require_api_key)])
async def generate_image(request: ImageGenerationRequest):
    return await generator.generate(request)

@router.post("/warmup")
async def warmup():
    await generator._manager.ensure_loaded()
    return {"ok": True}