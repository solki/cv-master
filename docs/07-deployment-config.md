# Deployment And Configuration

## Docker Compose Services

MVP Docker Compose should include:

- `api`: FastAPI backend
- `worker`: Celery worker
- `web`: Next.js frontend
- `postgres`: Postgres with pgvector
- `redis`: Celery broker and result backend
- `adminer`: database management UI

## Ports

Suggested local ports:

- Web: `3000`
- API: `8000`
- Postgres: `5432`
- Redis: `6379`
- Adminer: `8080`

## Required Environment Variables

```env
LLM_PROVIDER=openai_compatible

OPENAI_COMPATIBLE_API_KEY=
OPENAI_COMPATIBLE_BASE_URL=https://api.deepseek.com
OPENAI_COMPATIBLE_MODEL=deepseek-v4-pro
OPENAI_COMPATIBLE_PROVIDER_NAME=deepseek

OPENAI_API_KEY=
OPENAI_MODEL=

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=

TAVILY_API_KEY=

DATABASE_URL=postgresql+asyncpg://cv_master:cv_master@postgres:5432/cv_master
POSTGRES_USER=cv_master
POSTGRES_PASSWORD=cv_master
POSTGRES_DB=cv_master

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

VAULT_PATH=/app/vault
GENERATED_FILES_PATH=/app/generated
```

## Provider Selection

Provider selection should be centralized in backend settings.

Rules:

- `LLM_PROVIDER=openai_compatible` uses `OPENAI_COMPATIBLE_*`.
- `LLM_PROVIDER=openai` uses `OPENAI_*`.
- `LLM_PROVIDER=anthropic` uses `ANTHROPIC_*`.
- `LLM_PROVIDER=ollama` uses `OLLAMA_*`.

The app should validate required variables on startup and expose provider health through `/health/llm`.

## Adminer

Adminer should be available in local development for direct database inspection. It should not be exposed publicly in production-like deployments.

## Local Data

Use Docker volumes for:

- Postgres data
- Redis data if persistence is desired
- Markdown vault
- generated files

## Future Packaging Options

Phase 2 can consider:

- desktop wrapper
- local app bundle
- background agent process
- optional remote sync
- encrypted backup

