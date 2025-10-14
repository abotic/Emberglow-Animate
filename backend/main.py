from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .core.config import get_settings
from .core.logging import setup_logging
from .api.routers import image, system
from .services.warmup_service import warmup_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.setup_environment()
    setup_logging()
    
    if settings.auto_warmup:
        await warmup_service.ensure_warmup_started()
    
    yield


app = FastAPI(
    title="AI Image Generation Service",
    version="2.0.0",
    lifespan=lifespan
)

settings = get_settings()
settings.setup_environment()

cors_origins = [origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory=settings.output_dir), name="files")

app.include_router(image.router)
app.include_router(system.router)

if settings.enable_video:
    from .api.routers import video
    app.include_router(video.router)

if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")