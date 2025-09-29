import gc
import torch
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Any
from ..core.device import DeviceManager, DeviceType
from ..core.logging import get_logger

class BaseModelManager(ABC):
    def __init__(self, hf_token: Optional[str] = None):
        self.pipe: Optional[Any] = None
        self.hf_token = hf_token
        self._lock = asyncio.Lock()
        self.device: DeviceType = DeviceManager.get_device()
        self.logger = get_logger(self.__class__.__name__)
        
        DeviceManager.setup_cuda_optimizations()
    
    def unload(self) -> None:
        """Free model from memory"""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self.logger.info("Model unloaded")
    
    @abstractmethod
    async def ensure_loaded(self) -> None:
        """Load model if not already loaded"""
        pass
    
    @abstractmethod
    async def infer(self, **kwargs) -> Any:
        """Run inference"""
        pass