# CV Master

CV Master is a local-first AI agent for generating job-targeted resumes from a user's career knowledge base. The MVP is designed for a single user, private deployment, and high-quality resume generation across PDF, Markdown, HTML, and Word outputs.

The long-term direction is a specialized personal career assistant, not a generic SaaS product. The architecture therefore prioritizes modular agent workflows, durable personal knowledge, provider-agnostic LLM access, and auditable resume claims.

---

## Quick Start (First Time Setup)

Follow these steps to get CV Master running on your machine.

### Prerequisites

| Dependency | Minimum Version | Check Command |
|---|---|---|
| Docker + Docker Compose | Docker 24+, Compose v2 | `docker --version && docker compose version` |
| Git | 2.x | `git --version` |

**Optional** (for local development without Docker):

| Dependency | Minimum Version | Check Command |
|---|---|---|
| Python | 3.12+ | `python --version` |
| Node.js | 22+ | `node --version` |
| npm | 10+ | `npm --version` |

### Step 1: Clone the Repository

```bash
git clone https://github.com/solki/cv-master.git
cd cv-master
```

### Step 2: Create Environment Configuration

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` and configure at minimum:

- **LLM Provider** — set `LLM_PROVIDER` and the corresponding API key + model. Supported providers:

  | Provider | Required Variables |
  |---|---|
  | `openai_compatible` (DeepSeek, etc.) | `OPENAI_COMPATIBLE_API_KEY`, `OPENAI_COMPATIBLE_BASE_URL`, `OPENAI_COMPATIBLE_MODEL` |
  | `openai` | `OPENAI_API_KEY`, `OPENAI_MODEL` |
  | `anthropic` | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` |
  | `ollama` (local) | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` |

- **Search** (optional but recommended for JD analysis) — set `TAVILY_API_KEY` for web search during job description research.

The database and Redis variables are pre-configured for Docker Compose and do not need to be changed.

### Step 3: Start the Services (Docker)

```bash
docker compose -f docker/docker-compose.yml up --build
```

This builds and launches all 6 services:

| Service | URL | Purpose |
|---|---|---|
| **api** | http://localhost:8000 | FastAPI backend |
| **web** | http://localhost:3000 | Next.js frontend |
| **worker** | — | Celery async task worker |
| **postgres** | localhost:5432 | PostgreSQL 16 + pgvector |
| **redis** | localhost:6379 | Celery broker + cache |
| **adminer** | http://localhost:8080 | Database inspection GUI |

Wait for all services to become healthy (the `api` service waits for Postgres before starting). The first build may take a few minutes to download images and install dependencies.

### Step 4: Run Database Migrations

In a **separate terminal**, while the services are running:

```bash
# Generate the initial migration (first time only)
docker compose -f docker/docker-compose.yml exec api alembic revision --autogenerate -m "initial"

# Apply all pending migrations
docker compose -f docker/docker-compose.yml exec api alembic upgrade head
```

The `alembic upgrade head` command creates all tables (career entities, JDs, resumes, ingestion records, embeddings) in Postgres.

### Step 5: Verify the Installation

```bash
# Check API health (includes database connectivity)
curl http://localhost:8000/health

# Check LLM provider status
curl http://localhost:8000/health/llm

# Open the frontend in your browser
open http://localhost:3000
```

The `/health` endpoint returns:
```json
{
  "status": "ok",
  "environment": "development",
  "database": {"status": "connected"}
}
```

### Step 6: Start Using CV Master

1. Open **http://localhost:3000** in your browser.
2. Go to **Career Profile** — fill in your name, headline, location, and contact info.
3. Go to **Projects** — add past projects with roles, skills, and descriptions.
4. Go to **Evidence** — upload supporting materials (metrics, artifacts, feedback).
5. Go to **JD Analyzer** — paste a job description, fetch one from a URL, or upload a Markdown file.
6. Go to **Resume Generator** — select a JD and generate a targeted resume.
7. Go to **Resume Library** — browse, review, and export your generated resumes.

---

## Alternative: Local Development Without Docker

Use this path if you prefer running services directly on your machine.

### Prerequisites

- Python 3.12+, Node.js 22+, PostgreSQL 16 with pgvector extension, Redis 7+

### Backend Setup

```bash
cd apps/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment for localhost
export DATABASE_URL=postgresql+asyncpg://cv_master:cv_master@localhost:5432/cv_master
export DATABASE_URL_SYNC=postgresql+psycopg2://cv_master:cv_master@localhost:5432/cv_master
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/1
export VAULT_PATH=./vault
export GENERATED_FILES_PATH=./generated

# Run migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000

# In another terminal, start the Celery worker
source venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend Setup

```bash
cd apps/web

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open **http://localhost:3000** in your browser.

### Run Tests

```bash
# Backend tests (uses SQLite — no Postgres needed)
cd apps/api
source venv/bin/activate
pytest                                    # all tests
pytest tests/test_health.py               # single file
pytest -k "test_settings"                 # by keyword

# Frontend build check
cd apps/web
npm run build
```

---

## Project Structure

```text
apps/
  api/                          Python FastAPI backend
    app/
      api/routes/               REST endpoints (career entities, JDs, resumes, ingestion, retrieval, exports)
      agents/                   LangGraph resume generation workflow (7-node StateGraph)
      core/                     Settings (Pydantic), logging (structlog)
      db/                       Async SQLAlchemy engine, session, base model
      exports/                  Renderer: JSON → Markdown → HTML → PDF → DOCX
      knowledge/                Embedding service, hybrid semantic + keyword retrieval
      llm/                      Provider adapters (openai_compatible, openai, anthropic, ollama)
      models/                   SQLAlchemy models (15 entities + pgvector embeddings)
      schemas/                  Pydantic request/response schemas
      search/                   Tavily search adapter
    alembic/                    Database migrations
    tests/                      pytest + SQLite integration tests
  web/                          Next.js 14 frontend
    app/                        App Router pages (dashboard, profile, projects, evidence, JD, resumes, library, vault, settings)
    lib/                        API client, TypeScript types, Zustand store
docker/                         Docker Compose configuration
docs/                           Planning and design documents
knowledge-vault/                Local Markdown mirror for human-readable career data
```

---

## Environment Variables Reference

Full list of available variables (see `.env.example`):

| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_ENV` | No | `development` | `development` or `production` |
| `LLM_PROVIDER` | **Yes** | `openai_compatible` | LLM provider selection |
| `OPENAI_COMPATIBLE_API_KEY` | Per provider | — | API key for OpenAI-compatible endpoint |
| `OPENAI_COMPATIBLE_BASE_URL` | Per provider | — | Base URL (e.g. `https://api.deepseek.com`) |
| `OPENAI_COMPATIBLE_MODEL` | Per provider | — | Model name (e.g. `deepseek-v4-pro`) |
| `OPENAI_API_KEY` | Per provider | — | OpenAI API key |
| `OPENAI_MODEL` | Per provider | — | Model name (e.g. `gpt-4o`) |
| `ANTHROPIC_API_KEY` | Per provider | — | Anthropic API key |
| `ANTHROPIC_MODEL` | Per provider | — | Model name (e.g. `claude-sonnet-4-6`) |
| `OLLAMA_BASE_URL` | Per provider | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | Per provider | — | Model name (e.g. `llama3`) |
| `TAVILY_API_KEY` | No | — | Tavily search API key (for JD research) |
| `DATABASE_URL` | **Yes** | Docker default | Async Postgres connection string |
| `DATABASE_URL_SYNC` | No | Docker default | Sync Postgres connection (Alembic) |
| `CORS_ORIGINS` | No | `["http://localhost:3000"]` | Allowed CORS origins |

---

## Documentation Map

- [AGENTS.md](./AGENTS.md): Operating guide for future coding agents.
- [Product Requirements](./docs/01-product-requirements.md): MVP scope, user journeys, and success criteria.
- [System Architecture](./docs/02-system-architecture.md): Backend, frontend, services, and deployment topology.
- [Data Model](./docs/03-data-model.md): Core entities and database design.
- [Agent Workflows](./docs/04-agent-workflows.md): Resume generation graph and supporting agent workflows.
- [API Design](./docs/05-api-design.md): REST API surface for the MVP.
- [Frontend Plan](./docs/06-frontend-plan.md): Screens, interaction model, and UI stack.
- [Deployment and Configuration](./docs/07-deployment-config.md): Docker-based local deployment plan with Postgres and Adminer.
- [Security and Privacy](./docs/08-security-privacy.md): Privacy posture, secrets, and network-call rules.
- [Testing and Quality](./docs/09-testing-quality.md): Unit, integration, agent, export, and UI test plan.
- [Roadmap](./docs/10-roadmap.md): MVP and post-MVP phases.
- [Development Task Breakdown](./docs/11-development-task-breakdown.md): Milestone-level tasks with acceptance criteria.
- [Knowledge Base ADR](./docs/adr/0001-knowledge-base-architecture.md): Obsidian, QBrain-style, and Mem0-style comparison with the recommended approach.
- [LLM Provider ADR](./docs/adr/0002-llm-provider-strategy.md): Provider abstraction, environment variables, and Tavily integration.
- [Primary Design Spec](./docs/superpowers/specs/2026-06-04-cv-master-design.md): Consolidated design specification.

## Target Stack

- Backend: Python, FastAPI, LangGraph, SQLAlchemy 2, Alembic, Pydantic Settings.
- Data: Postgres, pgvector, Redis.
- Async jobs: Celery.
- Frontend: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Zustand.
- Search: Tavily for MVP, behind a replaceable search provider interface.
- LLMs: OpenAI-compatible APIs, OpenAI, Anthropic, and Ollama via `LLM_PROVIDER`.

## MVP Principle

The resume agent must optimize for recruiter and ATS screening while staying grounded in the user's real career evidence. Generated claims should be traceable to stored career facts, projects, achievements, or evidence records.
