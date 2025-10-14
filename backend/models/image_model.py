import asyncio
import warnings
from typing import Optional, Dict, Any, List
import torch
from diffusers import DiffusionPipeline
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast

from ..core.config import get_settings
from ..core.device import DeviceManager
from ..core.exceptions import ModelLoadError, GenerationError
from .base import BaseModelManager


class ImageModelManager(BaseModelManager):
    def __init__(self, hf_token: Optional[str] = None):
        super().__init__(hf_token)
        self.settings = get_settings()
        self.repo_id = "stabilityai/stable-diffusion-3.5-medium"
        self.dtype = DeviceManager.get_dtype(self.device, self.settings.force_fp16)
        self.variant = "fp16" if self.device == "cuda" else None

    def _configure_pipeline(self, pipe: DiffusionPipeline) -> DiffusionPipeline:
        try:
            if hasattr(pipe, "enable_vae_slicing"):
                pipe.enable_vae_slicing()
            if hasattr(pipe, "enable_vae_tiling"):
                pipe.enable_vae_tiling()
        except Exception as e:
            self.logger.warning(f"Failed to enable VAE optimizations: {e}")
        return pipe

    async def ensure_loaded(self) -> None:
        async with self._lock:
            if self.pipe is not None:
                return
            self.logger.info(f"Loading model {self.repo_id}")
            loop = asyncio.get_running_loop()
            try:
                self.pipe = await loop.run_in_executor(None, self._load_pipeline)
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

    def _collect_tokenizers(self) -> List[tuple[str, Any]]:
        tks: List[tuple[str, Any]] = []
        for name in ("tokenizer", "tokenizer_2", "tokenizer_3"):
            tk = getattr(self.pipe, name, None)
            if tk is not None:
                tks.append((name, tk))
        return tks

    def _measure_tokens(self, prompt: str) -> List[Dict[str, Any]]:
        info: List[Dict[str, Any]] = []
        for name, tk in self._collect_tokenizers():
            try:
                if not isinstance(tk, (PreTrainedTokenizer, PreTrainedTokenizerFast)):
                    continue
                out = tk(prompt, add_special_tokens=True, truncation=False)
                ids = out["input_ids"]
                length = len(ids) if isinstance(ids, list) else len(ids[0])
                max_len = getattr(tk, "model_max_length", 77)
                info.append({
                    "tokenizer": name,
                    "length": int(length),
                    "max_length": int(max_len),
                    "will_truncate": bool(length > max_len)
                })
            except Exception as e:
                info.append({"tokenizer": name, "error": f"token length measure failed: {e}"})
        return info

    async def infer_batch_same_shape(
        self,
        *,
        prompts: List[str],
        negative_prompts: List[Optional[str]],
        num_inference_steps: int,
        guidance_scale: float,
        width: int,
        height: int,
        seeds: Optional[List[Optional[int]]] = None,
        micro_batch_size: int = 4,
    ) -> List[Dict[str, Any]]:
        await self.ensure_loaded()

        N = len(prompts)
        assert len(negative_prompts) == N, "negative_prompts length mismatch"
        if seeds is None:
            seeds = [None] * N
        assert len(seeds) == N, "seeds length mismatch"

        token_info = self._measure_tokens(prompts[0]) if N > 0 else []
        out_all: List[Dict[str, Any]] = []

        loop = asyncio.get_running_loop()

        def _run_subbatch(
            p_sub: List[str],
            n_sub: List[Optional[str]],
            g_sub: List[Optional[torch.Generator]],
        ):
            sched_cls = self.pipe.scheduler.__class__
            self.pipe.scheduler = sched_cls.from_config(self.pipe.scheduler.config)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = self.pipe(
                    prompt=p_sub,
                    negative_prompt=n_sub,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    width=width,
                    height=height,
                    generator=g_sub,
                )
                warn_msgs = [str(x.message) for x in w]
            return result, warn_msgs

        try:
            async with self._infer_sem:
                for start in range(0, N, max(1, micro_batch_size)):
                    end = min(N, start + max(1, micro_batch_size))
                    p_sub = prompts[start:end]
                    n_sub = negative_prompts[start:end]
                    
                    sub_seeds = seeds[start:end]
                    if all(s is None for s in sub_seeds):
                        g_sub = None
                    else:
                        g_sub = []
                        for s in sub_seeds:
                            if s is None:
                                g_sub.append(torch.Generator(device=self.device))
                            else:
                                g_sub.append(torch.Generator(device=self.device).manual_seed(int(s)))

                    self.logger.info(
                        f"BATCH subrange {start}:{end} | size={end-start} | "
                        f"{width}x{height} steps={num_inference_steps} guide={guidance_scale}"
                    )
                    result, warn_msgs = await loop.run_in_executor(None, _run_subbatch, p_sub, n_sub, g_sub)

                    for i, img in enumerate(result.images):
                        out_all.append({
                            "image": img,
                            "warnings": warn_msgs,
                            "token_info": token_info,
                            "prompt": p_sub[i],
                            "negative_prompt": n_sub[i],
                            "seed": seeds[start + i],
                        })

            return out_all

        except Exception as e:
            raise GenerationError(f"Image batch generation failed: {e}")

    async def infer(self, **kwargs) -> Dict[str, Any]:
        res = await self.infer_batch_same_shape(
            prompts=[kwargs.get("prompt", "")],
            negative_prompts=[kwargs.get("negative_prompt")],
            num_inference_steps=kwargs.get("num_inference_steps", 44),
            guidance_scale=kwargs.get("guidance_scale", 7.5),
            width=kwargs.get("width", 1024),
            height=kwargs.get("height", 1024),
            seeds=[kwargs.get("seed")],
            micro_batch_size=1,
        )
        return res[0]