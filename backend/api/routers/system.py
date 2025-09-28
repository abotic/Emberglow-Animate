from fastapi import APIRouter
from ...services.warmup_service import warmup_service

router = APIRouter(prefix="/api", tags=["system"])

@router.get("/ready")
async def get_ready_status():
    return {"ready": warmup_service.ready}

@router.post("/warmup")
async def trigger_warmup():
    await warmup_service.ensure_warmup_started()
    return {"ok": True, "started": True}