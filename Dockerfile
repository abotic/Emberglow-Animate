FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/models \
    TRANSFORMERS_CACHE=/models \
    HF_HUB_DISABLE_TELEMETRY=1 \
    HF_HUB_ENABLE_HF_TRANSFER=1 \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True \
    TORCH_ALLOW_TF32=1

# System deps (ffmpeg for video, node 20 to build frontend)
RUN apt-get update && \
    apt-get install -y ffmpeg git curl build-essential && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Backend requirements first (better caching)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY backend ./backend
COPY frontend ./frontend

# Build frontend (Vite) -> /app/frontend/dist
WORKDIR /app/frontend
RUN npm ci && npm run build

# Back to app root
WORKDIR /app

# Expose FastAPI
EXPOSE 8000

# Health & performance envs (optional)
ENV UVICORN_WORKERS=1 \
    UVICORN_PORT=8000 \
    UVICORN_HOST=0.0.0.0

# Start the server
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
