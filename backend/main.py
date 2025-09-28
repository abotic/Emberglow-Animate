from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .core.config import get_settings
from .core.logging import setup_logging
from .api.routers import image, video, system
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
    title="AI Media Service",
    version="2.0.0",
    lifespan=lifespan
)

settings = get_settings()

cors_origins_list = [origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/files", StaticFiles(directory=settings.output_dir), name="files")

# Include routers
app.include_router(image.router)
app.include_router(video.router)
app.include_router(system.router)

# Serve frontend if built
if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")