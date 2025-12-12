# 🤖 RAG Pipeline + RQ Workers

## Overview
This project implements a Retrieval-Augmented Generation (RAG) pipeline with:
- Local embeddings using **Ollama (nomic-embed-text)**
- Vector storage via **Qdrant**
- Retrieval using **Gemini API / OpenAI SDK**
- Async API server using **FastAPI + Uvicorn**
- Background + parallel job execution using **RQ (Redis Queue)**

Goal: Retrieve context from a PDF, embed + index it, then answer user queries using grounded retrieval.

---

# ⚙️ Worker Setup (RQ on Windows, Linux, macOS)

## RQ on Different OS
### Linux / macOS
- Python supports `os.fork()`, so the default RQ worker works.
- To run a worker:
```bash
rq worker YOUR_QUEUE_NAME
```
- If using macOS and you get fork safety errors:
```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
rq worker YOUR_QUEUE_NAME
```

### Windows
Windows does **not support `fork()`**, so:
- You **must** use `SimpleWorker`(recommended) or `SpawnWorker`. (this can further fail due to os.wait4() command not being available)

#### 1. SpawnWorker (for running `worker.py`)
```bash
rq worker -w rq.worker.SpawnWorker
```

#### 2. SimpleWorker (recommended for Windows dev)
```bash
rq worker -w rq.worker.SimpleWorker
```

#### Worker Pool (Windows) 
#### helps in running queries in true parallelism.
```bash
rq worker-pool -w rq.worker.SimpleWorker -n 3
```

---

# 🔧 RQ Important Notes

## Redis URL config
RQ assumes:
```
redis://localhost:6379
```
If you're using a different port/domain:
```bash
rq worker -w rq.worker.SimpleWorker --url redis://YOUR_HOST:YOUR_PORT
```

## Worker Status
Check how many workers are running:
```bash
rq info
```

If Redis (Valkey) was stopped and workers still show up:
- They will be auto-removed after **420 seconds** (zombie cleanup).

---

# 📦 Job Registries (Success & Failure)

## Success Registry
- Completed jobs go here.
- Default TTL = **500 seconds**
- After TTL expiry → Redis deletes them to save memory.

## Failure Registry
- Failed jobs go here.
- They **do not** have TTL by default.
- You can:
  - Retry them
  - Delete manually
  - Set custom TTL

---

# 🧠 Project Context (Your Architecture)

You built a custom RAG pipeline using:
- **RQ** → concurrency + parallelism
- **Ollama** (nomic-embed-text) → local embeddings
- **Gemini API** & **OpenAI SDK** → retrieval + generation
- **LangChain** → indexing, chunking, document loading
- **Qdrant** → vector storage
- **FastAPI + Uvicorn** → async API service

---

# 🗂 Project Structure (Suggested)
- `components/`
  - `index.py` — load → chunk → embed → store in Qdrant
  - `redis_client.py` — initiallize redis client for enqueuing jobs.
  - `worker.py` — RQ worker code
  - `nodejs.pdf` — example document
- `main.py` — API entry point
- `.env` — secrets, API keys
- `docker-compose.yml` — Qdrant setup
- `pyproject.toml` / `uv.lock` — dependencies

---

# 🚀 Setup & Installation

## 1. Install uv
```bash
pip install uv
```

## 2. Create Virtual Environment
```bash
uv venv
```

Activate it:

**Linux / macOS**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

Install dependencies:
```bash
uv sync
```

---

## 3. Add API Keys
Inside `.env`:
```env
GEMINI_API_KEY=""
OPENAI_API_KEY=""
QDRANT_URL="http://localhost:6333"
```

---

# 📄 Document Indexing (Ollama + Qdrant)

## Requirements/ Prerequisite
- Docker installed
- nomic-embed-text model pulled

## Steps

### 1. Start Qdrant, ollama and valkey
```bash
docker compose up -d
```

### 2. Run indexing
```bash
uv run components/index.py
```

---

# 🔍 Retrieval (Gemini / OpenAI + Qdrant) By 🧵 Running the API Server

You can adjust:
- chunk size
- chunk overlap
- top-k retrieved documents

inside the script.
 
```bash
uvicorn main:app --reload
```
- go to localhost:8080/docs and try out the /chat and /job-status endpoints.
---

# 🧩 Summary
You now have:
- Local embeddings
- Local vector database
- RQ-powered async workers
- Gemini/OpenAI retrieval
- Fully functional RAG pipeline
- Cross-platform worker support



























for windows to run the worker.py we have to do: rq worker -w rq.worker.SpawnWorker     || as it avoids the fork() call which is not available in windows.
it still shows error for os.wait4() command, so i am pivoting to gevent instead of native os module to run the rq low level commands.
gevent doesnt work for me

On Linux / macOS, Python can use os.fork() to create new processes.

On Windows, there is no fork() — Windows uses a different multiprocessing start method.
For development on Windows → use SimpleWorker.
rq by default thinks that the redis server is running at localhost:6379 so if you have some other port or domain, then pass the config in cli with --url flag.

command: rq worker -w rq.worker.SimpleWorker  to start one worker

to start worker pool, so more req can be processed parallelly, command: rq worker-pool -w rq.worker.SimpleWorker -n 3
to know how many workers are running, command: rq info 
if you have stopped the valkey instance and the command rq info still shows workers, then they will be removed in 420 sec while cleaning up zombie workers.


after job completion, job moves to one of the two redis registeries: success and failures.
succeed jobs have ttl of default 500 sec, after that they are removed by redis for storage efficiency.
failed jobs can be retried or removed completely but they dont have a ttl by default, we can set that manually though.

for os , first run the export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
after that run rq worker YOUR_QUEUE_NAME