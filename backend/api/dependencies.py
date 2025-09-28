from fastapi import Header, HTTPException, Depends
from typing import Optional
from ..core.config import Settings, get_settings

async def require_api_key(
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings)
) -> None:
    if not settings.api_key:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization")
    if authorization.split(" ", 1)[1].strip() != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")