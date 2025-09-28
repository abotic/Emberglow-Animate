# 🔥 Emberglow Animate

Emberglow Animate is a full-stack AI application for generating stunning images with Stable Diffusion 3.5 and animating them into seamless video loops. It features a clean React frontend and a powerful, async Python backend built with FastAPI.

!

---

## ✨ Features

* **Text-to-Image Generation:** Utilizes the powerful **Stable Diffusion 3.5 Large** model for high-quality image creation.
* **Image-to-Video Animation:** Animate any image into a smooth, looping video clip (feature code is present).
* **Style Presets:** Easily guide the image style with presets like Cinematic, Photographic, Anime, and more.
* **Async Job Queue:** Video tasks are handled in the background, allowing the UI to remain responsive.
* **Modern Tech Stack:** Built with FastAPI, React, TypeScript, and Tailwind CSS.
* **Dockerized for Deployment:** Comes with a complete `Dockerfile` ready for deployment on services like RunPod.

---

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Git
* Docker & Docker Compose
* Node.js (v20+) and npm
* Python (v3.11+) and pip

### Configuration

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/abotic/emberglow-animate.git](https://github.com/abotic/emberglow-animate.git)
    cd emberglow-animate
    ```

2.  **Create your environment file:**
    Copy the example environment file to a new file named `.env`.
    ```bash
    cp .env.example .env
    ```

3.  **Edit `.env`:**
    Open the `.env` file and add your secret **Hugging Face Token**. You must have been granted access to the [stabilityai/stable-diffusion-3.5-large](https://huggingface.co/stabilityai/stable-diffusion-3.5-large) model hub for this to work.
    ```env
    HF_TOKEN=hf_YourSecretTokenHere
    API_KEY=your_optional_secret_api_key
    ```

---

## 🐳 Deployment (Docker - Recommended)

This is the easiest way to run the entire application.

1.  **Build the Docker image:**
    ```bash
    docker build -t emberglow-animate .
    ```

2.  **Run the container:**
    This command starts the application, maps the port, and uses local folders (`./models` and `./outputs`) to persist the AI models and generated videos, which is crucial.
    ```bash
    docker run --rm -p 8000:8000 --gpus all \
      -v ./models:/app/models \
      -v ./outputs:/app/outputs \
      --env-file .env \
      emberglow-animate
    ```

3.  **Access the app:** Open your browser to `http://localhost:8000`.

---

## 💻 Local Development

Follow these steps to run the backend and frontend separately.

### Backend

1.  **Navigate to the project root.**
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the server:**
    The server will start on `http://localhost:8000`.
    ```bash
    python -m uvicorn backend.main:app --reload --port 8000
    ```

### Frontend

1.  **In a new terminal, navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
3.  **Run the development server:**
    The UI will be available at `http://localhost:5173` and will proxy API requests to the backend.
    ```bash
    npm run dev
    ```

---

## 🔌 API Usage

You can also interact with the API directly.

**Endpoint:** `POST /api/image/generate`

**Headers:**
* `Content-Type: application/json`
* `Authorization: Bearer your_api_key` (if set)

**Example `curl` request:**
```bash
curl -X POST http://localhost:8000/api/image/generate \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_api_key" \
-d '{
  "prompt": "A cinematic photo of a robot drinking coffee in a Parisian cafe",
  "style": "Cinematic",
  "num_inference_steps": 50,
  "guidance_scale": 7.5,
  "width": 1024,
  "height": 1024
}'
```

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.