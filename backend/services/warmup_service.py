import asyncio
from typing import Dict, Optional
from ..core.logging import get_logger
from ..core.state import image_manager

class WarmupService:
    def __init__(self):
        self.ready: Dict[str, bool] = {"image": False, "video": False, "all": False}
        self._warmup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self.logger = get_logger(__name__)
    
    async def warmup(self) -> None:
        """Warm up the image model and keep it loaded."""
        self.logger.info("Starting warmup process for image model")
        
        try:
            await image_manager.ensure_loaded()
            
            self.ready["image"] = True
            self.ready["all"] = True
            self.logger.info("Warmup complete: Image model is loaded and ready.")
            
        except Exception as e:
            self.logger.error(f"Warmup failed: {e}")
            self.ready["all"] = False
    
    async def ensure_warmup_started(self) -> None:
        async with self._lock:
            if self._warmup_task and not self._warmup_task.done():
                self.logger.info("Warmup already in progress")
                return
            self._warmup_task = asyncio.create_task(self.warmup())

warmup_service = WarmupService()