import gc
import torch
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Any
from ..core.device import DeviceManager, DeviceType
from ..core.logging import get_logger
from ..core.config import get_settings


class BaseModelManager(ABC):
    def __init__(self, hf_token: Optional[str] = None):
        self.pipe: Optional[Any] = None
        self.hf_token = hf_token
        self._lock = asyncio.Lock()
        
        settings = get_settings()
        self._infer_sem = asyncio.Semaphore(settings.max_concurrent_image)
        
        self.device: DeviceType = DeviceManager.get_device()
        self.logger = get_logger(self.__class__.__name__)
        
        DeviceManager.setup_cuda_optimizations()

    def unload(self) -> None:
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self.logger.info("Model unloaded")

    @abstractmethod
    async def ensure_loaded(self) -> None:
        ...

    @abstractmethod
    async def infer(self, **kwargs) -> Any:
        ...