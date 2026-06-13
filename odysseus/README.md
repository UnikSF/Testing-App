# Odysseus for Docker

A self-hosted LLM chat interface based on [odysseus](https://github.com/pewdiepie-archdaemon/odysseus), packaged so that editing one `.env` file and running `docker compose up` gives you a fully working local AI chatbox with a model already downloaded and served.

## What it Does

- Runs the Odysseus web UI (chat interface) in a container
- Bundles Ollama as a sidecar service — no host-side model setup needed
- Downloads the configured model automatically on first start (persisted in a Docker volume, so subsequent starts are fast)
- Supports CPU, NVIDIA GPU, and AMD GPU configurations via compose overlays

## How to Start

### 1. Configure `.env`

Copy `.env.example` to `.env` and set at minimum:

```env
# Model(s) to pull and serve (space-separated for multiple)
OLLAMA_PULL_MODELS=qwen2.5:1.5b

# Use the bundled Ollama sidecar (Windows path separator)
COMPOSE_FILE=docker-compose.yml;docker/ollama.yml
```

For GPU support, append the right overlay:
- NVIDIA: `docker-compose.yml;docker/ollama.yml;docker/gpu.nvidia.yml`
- AMD:    `docker-compose.yml;docker/ollama.yml;docker/gpu.amd.yml`

### 2. Start

```bash
docker compose up
```

On first run, Docker pulls the images and Ollama downloads the model — this can take a few minutes depending on model size.

### 3. Open the UI

Navigate to `http://localhost:3000` (or the port configured in `.env`).

## Stopping

```bash
docker compose down
```

To also remove the downloaded model (forces re-download next time):
```bash
docker compose down -v
```

## Project Structure

```
docker/
  ollama.yml        — Ollama sidecar overlay
  gpu.nvidia.yml    — NVIDIA GPU passthrough
  gpu.amd.yml       — AMD GPU passthrough
  entrypoint.sh     — Startup script (pull models then serve)
docker-compose.yml  — Base compose file
.env.example        — Template for configuration
src/                — Odysseus app source
```
