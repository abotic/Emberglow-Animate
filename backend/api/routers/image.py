from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
import base64
import io
import os
import time
import asyncio
from collections import defaultdict
from PIL import Image

from ...models.schemas import ImageGenerationRequest, ArtStyle, BatchImageRequest
from ...core.exceptions import GenerationError
from ..dependencies import require_api_key
from ...core.state import image_manager
from ...core.logging import get_logger
from ...core.config import get_settings
from ...services.job_service import job_service, JobStatus

router = APIRouter(prefix="/api/image", tags=["image"])
logger = get_logger("image-api")
settings = get_settings()

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


def _enhance_prompt(prompt: str, style: ArtStyle) -> str:
    style_prompt = STYLE_PROMPTS.get(style, "")
    if style_prompt:
        return f"{prompt}, {style_prompt}, masterpiece, best quality"
    return prompt


def _encode_png(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def _save_png(img: Image.Image, out_dir: str, filename: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    img.save(path, format="PNG", optimize=True)
    rel = os.path.relpath(path, settings.output_dir).replace("\\", "/")
    return f"/files/{rel}"


@router.get("/status")
async def status() -> Dict[str, Any]:
    loaded = getattr(image_manager, "pipe", None) is not None
    return {"loaded": loaded, "pool": {"size": 1, "active": 0, "available": 1}}


@router.post("/generate", dependencies=[Depends(require_api_key)])
async def generate_image(request: ImageGenerationRequest) -> Dict[str, Any]:
    enhanced_prompt = _enhance_prompt(request.prompt, request.style)
    negative = request.negative_prompt or DEFAULT_NEGATIVE
    
    logger.info(
        "Image request: %dx%d steps=%d guidance=%.2f seed=%s | prompt=%r",
        request.width, request.height, min(request.num_inference_steps, 120),
        request.guidance_scale, request.seed, enhanced_prompt
    )
    
    try:
        out = await image_manager.infer(
            prompt=enhanced_prompt,
            negative_prompt=negative,
            num_inference_steps=min(request.num_inference_steps, 120),
            guidance_scale=request.guidance_scale,
            width=request.width,
            height=request.height,
            seed=request.seed
        )
    except Exception as e:
        logger.error("Single generation error: %s", e)
        raise GenerationError(f"Generation failed: {e}")

    return {
        "success": True,
        "image_url": _encode_png(out["image"]),
        "model_used": image_manager.repo_id,
        "width": request.width,
        "height": request.height,
        "num_inference_steps": request.num_inference_steps,
        "prompt": out.get("prompt"),
        "negative_prompt": out.get("negative_prompt"),
        "token_info": out.get("token_info", []),
        "warnings": out.get("warnings", []),
        "pool": {"size": 1, "active": 0, "available": 1},
    }


@router.post("/generate-batch", dependencies=[Depends(require_api_key)])
async def generate_batch(request: BatchImageRequest) -> Dict[str, Any]:
    if not request.items:
        return {"success": False, "error": "No items provided"}

    batch_id = request.prefix or f"batch_{int(time.time())}"
    out_dir = os.path.join(settings.output_dir, "batches", batch_id)
    micro_bsz = request.micro_batch_size

    groups: Dict[tuple, List[tuple[int, ImageGenerationRequest]]] = defaultdict(list)
    for idx, it in enumerate(request.items):
        groups[(it.width, it.height, min(it.num_inference_steps, 120), float(it.guidance_scale))].append((idx, it))

    results: List[Optional[Dict[str, Any]]] = [None] * len(request.items)

    try:
        for (w, h, steps, guide), pairs in groups.items():
            prompts, negs, seeds, indices = [], [], [], []
            for idx, it in pairs:
                indices.append(idx)
                prompts.append(_enhance_prompt(it.prompt, it.style))
                negs.append(it.negative_prompt or DEFAULT_NEGATIVE)
                if it.seed is not None:
                    seeds.append(it.seed)
                elif request.start_seed is not None:
                    seeds.append(request.start_seed + idx)
                else:
                    seeds.append(None)

            outs = await image_manager.infer_batch_same_shape(
                prompts=prompts,
                negative_prompts=negs,
                num_inference_steps=int(steps),
                guidance_scale=float(guide),
                width=int(w),
                height=int(h),
                seeds=seeds,
                micro_batch_size=micro_bsz,
            )

            for i, o in enumerate(outs):
                if request.save_to_disk:
                    url = _save_png(o["image"], out_dir, f"img_{indices[i]:04d}.png")
                    ref = {"file_url": url}
                else:
                    ref = {"image_url": _encode_png(o["image"])}
                results[indices[i]] = {
                    **ref,
                    "index": indices[i],
                    "seed": o.get("seed"),
                    "prompt": o.get("prompt"),
                    "negative_prompt": o.get("negative_prompt"),
                    "token_info": o.get("token_info", []),
                    "warnings": o.get("warnings", []),
                }

        packed = [r for r in results if r is not None]
        return {
            "success": True,
            "count": len(packed),
            "model_used": image_manager.repo_id,
            "batch_id": batch_id,
            "saved_to_disk": bool(request.save_to_disk),
            "results": packed,
            "pool": {"size": 1, "active": 0, "available": 1},
        }
    except Exception as e:
        logger.error("Batch generation error: %s", e)
        raise GenerationError(f"Batch generation failed: {e}")


async def _run_batch_job(job_id: str, request: BatchImageRequest) -> None:
    job_service.update_job(job_id, status=JobStatus.LOADING, progress=0.0)
    
    try:
        total = len(request.items)
        if total == 0:
            job_service.update_job(job_id, status=JobStatus.ERROR, error="No items provided")
            return

        batch_id = request.prefix or f"batch_{int(time.time())}"
        out_dir = os.path.join(settings.output_dir, "batches", batch_id)
        micro_bsz = request.micro_batch_size

        groups: Dict[tuple, List[tuple[int, ImageGenerationRequest]]] = defaultdict(list)
        for idx, it in enumerate(request.items):
            groups[(it.width, it.height, min(it.num_inference_steps, 120), float(it.guidance_scale))].append((idx, it))

        results: List[Optional[Dict[str, Any]]] = [None] * total
        processed = 0

        job_service.update_job(job_id, status=JobStatus.GENERATING, progress=0.0, metadata={"batch_id": batch_id})

        for (w, h, steps, guide), pairs in groups.items():
            prompts, negs, seeds, indices = [], [], [], []
            for idx, it in pairs:
                indices.append(idx)
                prompts.append(_enhance_prompt(it.prompt, it.style))
                negs.append(it.negative_prompt or DEFAULT_NEGATIVE)
                if it.seed is not None:
                    seeds.append(it.seed)
                elif request.start_seed is not None:
                    seeds.append(request.start_seed + idx)
                else:
                    seeds.append(None)

            outs = await image_manager.infer_batch_same_shape(
                prompts=prompts,
                negative_prompts=negs,
                num_inference_steps=int(steps),
                guidance_scale=float(guide),
                width=int(w),
                height=int(h),
                seeds=seeds,
                micro_batch_size=micro_bsz,
            )

            for i, o in enumerate(outs):
                if request.save_to_disk:
                    url = _save_png(o["image"], out_dir, f"img_{indices[i]:04d}.png")
                    ref = {"file_url": url}
                else:
                    ref = {"image_url": _encode_png(o["image"])}
                results[indices[i]] = {
                    **ref,
                    "index": indices[i],
                    "seed": o.get("seed"),
                    "prompt": o.get("prompt"),
                    "negative_prompt": o.get("negative_prompt"),
                    "token_info": o.get("token_info", []),
                    "warnings": o.get("warnings", []),
                }
                processed += 1
                job_service.update_job(job_id, status=JobStatus.GENERATING, progress=processed / total)

        packed = [r for r in results if r is not None]
        job_service.update_job(
            job_id,
            status=JobStatus.DONE,
            progress=1.0,
            result={
                "success": True,
                "count": len(packed),
                "model_used": image_manager.repo_id,
                "batch_id": batch_id,
                "saved_to_disk": bool(request.save_to_disk),
                "results": packed,
            },
        )
    except Exception as e:
        logger.error("Async batch job error: %s", e)
        job_service.update_job(job_id, status=JobStatus.ERROR, error=str(e))


@router.post("/generate-batch-async", dependencies=[Depends(require_api_key)])
async def generate_batch_async(request: BatchImageRequest) -> Dict[str, Any]:
    job_id = job_service.create_job(metadata={"type": "image-batch", "count": len(request.items)})
    asyncio.create_task(_run_batch_job(job_id, request))
    return {"ok": True, "job_id": job_id}


@router.get("/job/{job_id}")
async def get_job(job_id: str) -> Dict[str, Any]:
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/warmup")
async def warmup():
    await image_manager.ensure_loaded()
    return {"ok": True}