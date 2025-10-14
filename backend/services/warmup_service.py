import asyncio
from typing import Optional
from ..core.logging import get_logger
from ..core.state import image_manager


class WarmupService:
    def __init__(self):
        self._ready = False
        self._warmup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self.logger = get_logger(__name__)
    
    @property
    def ready(self) -> bool:
        return self._ready

    async def warmup(self) -> None:
        self.logger.info("Starting model warmup")
        try:
            await image_manager.ensure_loaded()
            self._ready = True
            self.logger.info("Warmup complete - model ready")
        except Exception as e:
            self.logger.error(f"Warmup failed: {e}")
            self._ready = False

    async def ensure_warmup_started(self) -> None:
        async with self._lock:
            if self._warmup_task and not self._warmup_task.done():
                self.logger.info("Warmup already in progress")
                return
            self._warmup_task = asyncio.create_task(self.warmup())


warmup_service = WarmupService()