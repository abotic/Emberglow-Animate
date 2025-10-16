# Emberglow Image Generation Service

> Production-ready bulk AI image generation for creators

### Emberglow Animate
[![Emberglow Animate](https://img.youtube.com/vi/ocjdzqJXIoM/maxresdefault.jpg)](https://www.youtube.com/watch?v=ocjdzqJXIoM)

## What is this?

Emberglow Animate is a high-performance image generation service designed for content creators who need to generate large batches of high-quality images. Whether you're creating assets for long-form videos, marketing materials, or visual storytelling projects, this service handles everything from single images to 100+ batch generations with intelligent queuing, progress tracking, and consistent quality.

Unlike basic SD wrappers, Emberglow is built specifically for **production workflows**. It intelligently groups requests by dimensions and settings, processes them efficiently with micro-batching, and gives you complete control over style, quality, and output format. Generate a single test image or queue up 500 scene illustrations—the system handles both.

## Why did I build this?

Creating visual content at scale is expensive and time-consuming. Commercial AI image APIs charge per image ($0.02-0.10 each), which adds up fast when you need hundreds of images for a video project or content series. A typical long-form video might need 100-200 scene illustrations, costing $20-100+ per video with commercial services.

I wanted a self-hosted solution that could:
- **Generate 100+ images efficiently** with intelligent batching
- **Maintain consistent quality** across large sets
- **Track progress in real-time** for long-running jobs
- **Integrate easily** with existing creative workflows

The result is a system that processes batch generations 3-5x faster than naive approaches, with full progress tracking and the ability to resume interrupted jobs.

## Features

### Core Generation
- **Single Image Generation**: Quick testing with real-time preview
- **Batch Processing**: Generate 1-10,000 images in a single request
- **Async Job Queue**: Long-running jobs with progress tracking
- **Smart Batching**: Automatically groups by dimensions/settings for optimal GPU utilization
- **Micro-batching**: Configurable batch sizes to prevent OOM on any GPU

### Styles & Quality
- **Art Styles**: Cinematic, Photographic, Anime, Fantasy, Digital Art, 3D, Neon Punk, Oil Painting, Watercolor, Freestyle
- **Quality Presets**: Fast (25 steps), Balanced (44 steps), High (64 steps), Ultra (84 steps)
- **Custom Parameters**: Full control over steps, guidance, dimensions, seeds
- **Negative Prompts**: Fine-tune what to avoid in generations

### Production Features
- **Real-Time Progress**: WebSocket-based progress updates for batch jobs
- **Seed Control**: Reproducible results with explicit seeds
- **Disk Storage**: Save images to disk with organized batch folders
- **Base64 Output**: Inline images for immediate use
- **Job Recovery**: Resume interrupted batch jobs
- **Token Analysis**: Preview prompt token usage across tokenizers

### Video Generation (Beta)
- **Image-to-Video**: Animate static images with SVD-XT (disabled by default)
- **Seamless Loops**: Perfect looping video generation
- **Frame Enhancement**: Optional bilateral filtering for quality
- **FFmpeg Integration**: Video encoding
- **Long-Form Support**: Generate videos from 30 seconds to hours

## Tech Stack

### Backend
- **Framework**: FastAPI 0.112+ with async/await
- **AI Model**: Stable Diffusion 3.5 Medium (9GB VRAM)
- **Video Model**: Stable Video Diffusion XT (optional)
- **Libraries**: PyTorch 2.4, Diffusers 0.32, Transformers 4.44
- **Optimization**: VAE slicing/tiling, FP16 precision, TF32 matmul

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS 3.4
- **Build**: Vite 5
- **API Client**: Axios with automatic retries

### Architecture
```
├── backend/
│   ├── api/
│   │   ├── routers/         # API endpoints
│   │   │   ├── image.py     # Image generation
│   │   │   ├── video.py     # Video (optional)
│   │   │   └── system.py    # Health checks
│   │   └── dependencies.py  # Auth middleware
│   ├── core/
│   │   ├── config.py        # Environment config
│   │   ├── device.py        # GPU detection
│   │   ├── state.py         # Model managers
│   │   └── logging.py       # Logging setup
│   ├── models/
│   │   ├── base.py          # Base manager
│   │   ├── image_model.py   # SD3.5 implementation
│   │   ├── video_model.py   # SVD implementation
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── job_service.py   # Job tracking
│       └── warmup_service.py # Model preloading
│
└── frontend/
    └── src/
        ├── components/      # React components
        ├── hooks/           # Custom hooks
        ├── services/        # API client
        └── types/           # TypeScript definitions
```

## Getting Started

### Prerequisites
- **GPU**: NVIDIA GPU with 12GB+ VRAM (RTX 3060+ recommended, H100 optimal)
- **CUDA**: 12.1+ with cuDNN 9
- **API Key**: Optional (for authentication)

### Option 1: One-Click RunPod Deployment (Recommended)

**Deploy in 60 seconds:**

1. **Create Template**
   - Go to [RunPod Templates](https://www.runpod.io/console/user/templates)
   - Click "New Template"
   - Configure:
     - **Container Image**: `antonio992/emberglow-animate-production`
     - **Container Disk**: 30 GB
     - **Volume Mount**: `/workspace`
     - **HTTP Ports**: `8000`

2. **Deploy Pod**
   - Select GPU: **H100** (optimal) or **RTX 4090** (great) or **RTX 3090** (minimum)
   - Choose "On-Demand" or "Spot"
   - Click "Deploy"

3. **Configure (Optional)**
   - Add environment variable: `API_KEY=your_secret_key`
   - Add: `ENABLE_VIDEO=true` (if you want video generation)

4. **Access**
   - Click HTTP port 8000
   - Wait ~30s for model warmup
   - Start generating!

**Performance by GPU:**
| GPU | VRAM | Batch Size | 100 Images | Cost/100 imgs* |
|-----|------|------------|------------|----------------|
| H100 | 80GB | 16 | ~8 min | ~$0.20 |
| RTX 4090 | 24GB | 6 | ~12 min | ~$0.10 |
| RTX 3090 | 24GB | 4 | ~18 min | ~$0.05 |

*Based on typical RunPod spot pricing

### Option 2: Docker (Local/VPS)

```bash
# Clone repository
git clone https://github.com/yourusername/emberglow-image-service.git
cd emberglow-image-service

# Configure
cp .env.example .env
# Edit .env with your settings

# Build and run
docker build --platform linux/amd64 -t emberglow-image .
docker run --gpus all -p 8000:8000 --env-file .env emberglow-image
```

Access at http://localhost:8000

### Option 3: Manual Installation (Development)

```bash
# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your HF_TOKEN

# Run
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Usage

### Quick Test (Single Image)

**UI:**
1. Open the web interface
2. Enter a prompt: "a serene mountain lake at sunset"
3. Select style: "Cinematic"
4. Click "Generate"

**API:**
```bash
curl -X POST http://your-runpod-url/api/image/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a serene mountain lake at sunset",
    "style": "Cinematic",
    "width": 1280,
    "height": 720,
    "num_inference_steps": 44
  }'
```

### Batch Generation (3 Images)

```bash
curl -X POST http://your-runpod-url/api/image/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"prompt": "ancient map with sea monsters", "style": "Cinematic", "width": 1280, "height": 720},
      {"prompt": "stormy ocean from ship deck", "style": "Cinematic", "width": 1280, "height": 720},
      {"prompt": "desert caravan at sunset", "style": "Cinematic", "width": 1280, "height": 720}
    ],
    "save_to_disk": true,
    "micro_batch_size": 4
  }'
```

### Large Batch (100+ Images, Async)

```bash
# Start job
curl -X POST http://your-runpod-url/api/image/generate-batch-async \
  -H "Content-Type: application/json" \
  -d @batch_request.json

# Response: {"ok": true, "job_id": "abc123"}

# Check progress
curl http://your-runpod-url/api/image/job/abc123

# Response includes progress: {"status": "generating", "progress": 0.45, ...}
```

### Long-Form Video Workflow

This is the real power for content creators. Generate scene illustrations for an entire video:

```python
import requests

# Your RunPod endpoint
API_BASE = "https://your-pod-8000.proxy.runpod.net"

# Scene prompts from your script (from separate story generator tool)
scenes = [
    {
        "prompt": "An aged vellum atlas on carved oak table, candlelight",
        "camera": "close-up, 50mm, shallow DOF",
        "lighting": "warm candlelight with deep shadows",
        "ar": "16:9",
        "seed": 10001
    },
    # ... 100+ more scenes
]

# Build batch request
items = []
for scene in scenes:
    items.append({
        "prompt": f"{scene['prompt']}, {scene['camera']}, {scene['lighting']}",
        "style": "Cinematic",
        "width": 1280,
        "height": 720,
        "num_inference_steps": 44,
        "seed": scene.get("seed")
    })

# Submit async job
response = requests.post(f"{API_BASE}/api/image/generate-batch-async", json={
    "items": items,
    "save_to_disk": True,
    "prefix": "my_video_project",
    "micro_batch_size": 6
})

job_id = response.json()["job_id"]

# Poll for completion
import time
while True:
    status = requests.get(f"{API_BASE}/api/image/job/{job_id}").json()
    print(f"Progress: {status['progress']:.1%}")
    if status["status"] == "done":
        print(f"Complete! {len(status['result']['results'])} images saved")
        break
    time.sleep(5)

# Images saved to: outputs/batches/my_video_project/
```

Then use the Flask video stitching tool (shown earlier) to combine these with narration into a final video.

## Environment Variables

### Backend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_TOKEN` | - | Hugging Face token (required for first download) |
| `API_KEY` | - | API authentication (optional) |
| `AUTO_WARMUP` | `true` | Load model on startup |
| `ENABLE_VIDEO` | `false` | Enable video generation endpoints |
| `MAX_CONCURRENT_IMAGE` | `1` | Concurrent inference limit |
| `FORCE_FP16` | `true` | Use FP16 precision (recommended) |
| `CORS_ORIGINS` | `*` | Allowed origins |

### Advanced Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTORCH_CUDA_ALLOC_CONF` | `max_split_size_mb:512,expandable_segments:True` | CUDA memory config |
| `HF_HUB_ENABLE_HF_TRANSFER` | `1` | Faster model downloads |

## Architecture Highlights

### Intelligent Batch Processing

Requests are automatically grouped by dimensions and settings:
```python
# Input: 100 mixed requests
[
  {width: 1280, height: 720, steps: 44},  # 60 images
  {width: 1024, height: 1024, steps: 44}, # 30 images
  {width: 1280, height: 720, steps: 64},  # 10 images
]

# Automatically grouped into 3 batches
# Each batch processed with optimal micro-batching
# 3-5x faster than sequential processing
```

### Micro-batching Strategy

Prevents OOM on any GPU:
- H100 (80GB): Batch size 16
- RTX 4090 (24GB): Batch size 6
- RTX 3090 (24GB): Batch size 4

Automatically pauses and resumes if memory pressure detected.

### Job Queue System

- Async processing with progress tracking
- Resume interrupted jobs (power loss, network issues)
- Multiple concurrent jobs (configurable)
- Real-time SSE updates or polling fallback

### Seed Management

- **No seed**: Random generation (different every time)
- **Explicit seed**: Reproducible results
- **start_seed + index**: Consistent batch with unique images

## Troubleshooting

**Model won't load**
- Check GPU: `nvidia-smi`
- Verify CUDA version: `nvcc --version`
- First run downloads 9GB model (takes 5-10 minutes)

**Generation fails with OOM**
- Reduce `micro_batch_size` in request
- Lower image dimensions (1024x1024 → 768x768)
- Check VRAM usage: `nvidia-smi`

**Slow generation**
- Expected: First image takes longer (model warmup)
- H100: ~3-5s per image (1280x720, 44 steps)
- RTX 4090: ~5-8s per image
- RTX 3090: ~8-12s per image

**Batch job stuck**
- Check job status: `/api/image/job/{job_id}`
- Review server logs for errors
- Jobs auto-resume on server restart if interrupted

## Integration Examples

### Python SDK
```python
from emberglow import ImageClient

client = ImageClient("https://your-pod.proxy.runpod.net")

# Single image
image = client.generate(
    prompt="cyberpunk city at night",
    style="Neon Punk",
    width=1280,
    height=720
)

# Batch async
job = client.batch_async(prompts, save_to_disk=True)
job.wait_until_complete()
print(f"Generated {len(job.results)} images")
```

### Node.js
```javascript
const axios = require('axios');

const API = 'https://your-pod.proxy.runpod.net';

async function generateImage(prompt) {
  const { data } = await axios.post(`${API}/api/image/generate`, {
    prompt,
    style: 'Cinematic',
    width: 1280,
    height: 720
  });
  return data.image_url; // base64 data URI
}
```

## Future Enhancements

- [ ] Multi-GPU support for parallel batching
- [ ] LoRA model loading
- [ ] ControlNet integration
- [ ] Upscaling pipeline (4x resolution)
- [ ] Inpainting/outpainting
- [ ] Video-to-video generation
- [ ] Custom model swapping (SDXL, Flux)
- [ ] Webhook notifications for job completion
- [ ] S3/cloud storage integration
- [ ] Advanced scheduling (priority queues)

## Contributing

Contributions welcome! This is a hobby project but improvements are appreciated:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Areas for help:**
- Performance optimizations
- Additional model support
- UI/UX improvements
- Documentation
- Bug fixes

## License

MIT License - see [LICENSE](LICENSE) file

## Credits

Built with:
- [Stable Diffusion 3.5](https://stability.ai) by Stability AI
- [Diffusers](https://github.com/huggingface/diffusers) by Hugging Face
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev) + [Vite](https://vitejs.dev) - Frontend
- [Tailwind CSS](https://tailwindcss.com) - Styling
- [PyTorch](https://pytorch.org) - Deep learning framework

## Acknowledgments

Special thanks to:
- Stability AI for Stable Diffusion 3.5 Medium
- Hugging Face for the Diffusers library
- The open-source AI community

---

For questions or issues, open a GitHub issue.
