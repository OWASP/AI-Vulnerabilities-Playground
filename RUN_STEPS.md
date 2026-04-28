# Run Steps (Local + Docker)

This is the single source of truth to run AIVP locally.

## Important: Strict Config Mode

Runtime config is now strict for active app paths:

- Backend requires env/config values (no silent fallback for core settings like `OLLAMA_URL`, `OLLAMA_MODEL`, `CORS_ORIGINS`, `SERVER_SALT`, `AIVP_DEFAULT_MODE`).
- Frontend contact form uses `VITE_CONTACT_EMAIL`.
- Missing required values can fail startup by design.

## Prerequisites (smooth lab access)

Whether you use **manual** dev servers or **Docker**, check these so chats, validation, and run tracking work without surprises.

- **Ollama on the host**  
  Install [Ollama](https://ollama.com), keep it running, and pull a model that matches `OLLAMA_MODEL` in your env (repo defaults to **`llama3.1`**):

  ```bash
  ollama pull llama3.1
  ```

  Labs call Ollama over HTTP; if the model is missing or Ollama is down, chat streams will fail or hang.

- **RAM / disk** (rough guide)  
  **16 GB+** system RAM and **~15 GB** free disk are comfortable for an 8B-class model, browser, and API. See `README.md` → Hardware for detail.

- **Ports**  
  - Manual: **8000** (API), **5173** (Vite), **11434** (Ollama).  
  - Docker: **80** on the host for the UI (override with `WEB_PORT` in `.env`). Ollama stays on the host (**11434** by default).

- **CORS**  
  The API only accepts origins listed in `CORS_ORIGINS`. For manual dev, include `http://localhost:5173`. For Docker, include `http://localhost` and `http://127.0.0.1` (see `.env.docker.example`).

- **Redis (optional but recommended)**  
  Run tracking and related features expect **Redis**. The Docker stack includes Redis automatically. For manual runs, start Redis locally or set `REDIS_URL` in `apps/api/.env`; if Redis is unreachable, some persistence features may degrade (core chat/validation still work if the API starts).

- **Same model name everywhere**  
  Use the same `OLLAMA_MODEL` value in the API env as the tag you pulled in Ollama (e.g. `llama3.1`).

---

## Option A — Manual (Python + Node)

### Prerequisites

- Python 3.10+ (3.12 works)
- Node.js 18+ (20 LTS recommended)
- Ollama installed (see above)

### 1) Start Ollama

```bash
ollama serve   # if not already running as a service
ollama pull llama3.1
```

### 2) Start Backend (FastAPI)

From repo root:

```bash
cd apps/api
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies and run:

```bash
pip install -r requirements.txt
cp .env.example .env   # on Windows: copy .env.example .env
uvicorn main:app --reload --port 8000
```

Required backend keys are documented in `apps/api/.env.example`. At minimum keep these set:
`OLLAMA_URL`, `OLLAMA_MODEL`, `CORS_ORIGINS`, `SERVER_SALT`, `AIVP_DEFAULT_MODE`, `ENABLE_TRAINING_LABS`, `OLLAMA_MODEL_TRAINING_LABS`.

Backend checks:

- API docs: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`

### 3) Start Frontend (Vite)

In a new terminal:

```bash
cd apps/web
npm install
cp .env.example .env   # on Windows: copy .env.example .env
npm run dev
```

For manual frontend dev, ensure `apps/web/.env` includes:
- `VITE_API_BASE=http://localhost:8000/api`
- `VITE_DEV_API_TARGET=http://localhost:8000`
- `VITE_CONTACT_EMAIL=avinash.kumar@owasp.org` (or your preferred destination)

Frontend URL:

- `http://localhost:5173`

### 4) Optional one-command launcher (Windows)

From repo root:

```powershell
.\install_lab.ps1
```

### 5) Common Issues (manual)

- `http://localhost:8000/` returns `{"detail":"Not Found"}`  
  - Expected. Use `/docs` or `/api/...` routes.
- CORS issue:
  - Ensure `apps/api/.env` has `CORS_ORIGINS=http://localhost:5173`
- If RAG (DE_10) is out-of-sync:
  - Stop backend
  - Remove local Chroma folder under `apps/api/chroma_db_*`
  - Restart backend

---

## Option B — Docker (one command)

Stack: **nginx** (static UI + reverse proxy **`/api` → API**), **FastAPI**, **Redis**. **Ollama stays on your machine** (not in the compose file), which keeps GPU access simple and avoids large model images.

### Prerequisites (Docker)

- **Docker Desktop** (Windows/macOS) or **Docker Engine 24+** with the **Compose plugin** (Linux).
- **Ollama on the host** — same as above: running service + `ollama pull llama3.1` (or your chosen model; set `OLLAMA_MODEL` in `.env`).
- **CPU / RAM** — Docker adds modest overhead; plan the same headroom as manual mode for Ollama.
- **Port 80 free** on the host, or set `WEB_PORT` (e.g. `8080:80` via `WEB_PORT=8080` in `.env`) if something else uses 80.
- **Reach host from containers** — Compose sets `extra_hosts: host.docker.internal:host-gateway` so the API container can call Ollama at `http://host.docker.internal:11434` (Docker Desktop, recent Linux). If that fails on an older Linux setup, set `OLLAMA_URL` to your host LAN IP.
- **`training_labs/Dockerfile` is optional** — you only need it for the separate training pipeline (`training_labs/train.py`), not for normal lab runtime.

### Steps

From the **repository root** (folder that contains `docker-compose.yml`):

```bash
cp .env.docker.example .env
# Edit .env if needed: OLLAMA_MODEL, WEB_PORT, SERVER_SALT, CORS_ORIGINS, VITE_CONTACT_EMAIL
docker compose up --build
```

Open **http://localhost** (or `http://localhost:<WEB_PORT>` if you changed it).

The frontend is built with `VITE_API_BASE=/api` so the browser talks to the **same origin**; nginx forwards `/api/*` to the API container. You do **not** need to expose port 8000 for normal use.

### Docker-specific issues

- **`http://localhost:8000` is unreachable from host** — Expected in this compose setup. The API service is internal-only (`expose: 8000`) and is accessed through nginx. Use `http://localhost` (or `http://localhost:<WEB_PORT>`) for the app.
- **Chat or validation fails immediately** — On the host, run `curl http://localhost:11434/api/tags` (or open Ollama UI). From inside the API container, Ollama must be reachable at `OLLAMA_URL` (default `http://host.docker.internal:11434`).
- **CORS errors in the browser** — Ensure `CORS_ORIGINS` in `.env` includes the exact origin you use (e.g. `http://localhost` without port for default port 80).
- **`chroma-hnswlib` build fails during image build** — This can happen more often on Python 3.12 slim images. Use `python:3.11-slim` for `apps/api/Dockerfile` and include `build-essential` so native wheel/source builds succeed.
- **RAG (DE_10) “Nope” after rebuild** — Chroma data inside the container is ephemeral unless you add a volume; wipe is equivalent to deleting `chroma_db_*` locally. Restart the API container after clearing.
- **Training labs (LoRA)** — Default compose sets `ENABLE_TRAINING_LABS=false`. Enable only if you have followed the training pipeline and tagged models in Ollama accordingly.
