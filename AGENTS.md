# AGENTS.md

This file is the operating guide for coding agents working on CV Master.

## Project Mission

CV Master is a local-first resume generation agent. Its MVP helps one user maintain a complete, auditable career knowledge base and generate ATS-friendly resumes tailored to a specific job description. The next phase should evolve toward a vertical personal assistant agent for career management, not a generic SaaS product.

The system must optimize for:

- truthful, evidence-backed resume content
- high compatibility with recruiter and ATS screening workflows
- user ownership of career data
- extensible agent workflows and provider-agnostic LLM integration
- clean handoff between coding agents

## Current Project State

This repository currently contains planning and architecture documentation only. There is no implemented application yet.

Recommended first implementation milestone:

1. Create the monorepo structure.
2. Implement Docker Compose for Postgres, Adminer, Redis, API, worker, and web.
3. Implement backend settings and health checks.
4. Add core database models and Alembic migrations.
5. Implement the first resume generation workflow end to end with one ATS-safe template.

## Planned Stack

Backend:

- Python 3.12+
- FastAPI
- LangGraph
- SQLAlchemy 2.x
- Alembic
- Pydantic and pydantic-settings
- Celery + Redis
- Postgres with pgvector
- Tavily API for MVP web/search tooling

Frontend:

- Next.js + React + TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Zustand
- React Hook Form + Zod
- TipTap or another mature Markdown editor

Document/export tooling:

- Markdown as canonical generated resume draft format
- HTML rendered from structured resume data/templates
- PDF rendered from HTML, preferably with Playwright or WeasyPrint after prototype validation
- DOCX rendered with a Python document library or Pandoc-compatible pipeline

## Repository Structure To Create

Use this target structure unless an approved implementation plan changes it:

```text
cv_master/
  AGENTS.md
  README.md
  docker-compose.yml
  .env.example
  apps/
    api/
      app/
        api/
        core/
        db/
        models/
        schemas/
        services/
        agents/
        workers/
        templates/
      alembic/
      tests/
      pyproject.toml
    web/
      app/
      components/
      lib/
      stores/
      styles/
      tests/
      package.json
  docs/
  vault/
    career/
    evidence/
    generated/
```

## Environment Contract

The backend must select the active model provider through `LLM_PROVIDER`.

Required provider modes:

- `openai_compatible`
- `openai`
- `anthropic`
- `ollama`

Use these environment variables:

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
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

Do not hard-code provider names, model names, API keys, or local paths.

## Data Integrity Rules

Resume generation must be evidence-backed.

- Every generated claim should trace to at least one stored career fact, project, experience, or evidence record.
- The system should distinguish user-provided facts from AI-inferred phrasing.
- The agent must not invent employers, titles, degrees, dates, metrics, certifications, or technologies.
- If a useful metric is missing, the agent should ask the user to provide it or generate a clearly marked suggestion for user approval.
- Store generated resume versions and their source evidence references.

## Architecture Principles

- Keep the backend API, agent workflows, retrieval engine, export service, and provider adapters separate.
- Treat Postgres as the source of truth for structured career data.
- Treat the Markdown vault as a local-readable knowledge layer, not the only source of truth.
- Use hybrid retrieval: semantic vector search plus keyword/full-text search.
- Avoid framework lock-in inside domain services. LangGraph nodes should call plain service interfaces.
- Design for one user in MVP, but leave room for account/profile scoping in phase 2.
- Keep generated content reproducible: record prompt version, model provider, model name, input JD hash, selected evidence, and output format.

## Development Conventions

- Prefer small modules with explicit interfaces.
- Use typed Pydantic schemas for API inputs/outputs and LLM structured outputs.
- Use Alembic for all schema changes.
- Use async SQLAlchemy in FastAPI request paths.
- Use Celery for long-running generation and export work.
- Keep frontend pages focused on workflows, not marketing pages.
- Do not add billing, multi-tenant SaaS features, or generic assistant capabilities in MVP unless explicitly requested.

## Planned Command Contract After Implementation Starts

Implement the project so these commands work, or update this section with the actual equivalents:

```bash
docker compose up --build
docker compose run --rm api alembic upgrade head
docker compose run --rm api pytest
docker compose run --rm web npm test
docker compose run --rm web npm run lint
```

Update this file when the actual commands differ.

## Documentation Map

- `README.md`: project overview and quick start direction.
- `docs/01-product-requirements.md`: MVP scope and product requirements.
- `docs/02-system-architecture.md`: technical architecture.
- `docs/03-data-model.md`: core entities and relationships.
- `docs/04-agent-workflows.md`: agent workflow design.
- `docs/05-api-design.md`: planned API endpoints.
- `docs/06-frontend-plan.md`: frontend screens and UX structure.
- `docs/07-deployment-config.md`: Docker and configuration plan.
- `docs/08-security-privacy.md`: privacy, security, and data handling.
- `docs/09-testing-quality.md`: test strategy and quality gates.
- `docs/10-roadmap.md`: staged implementation roadmap.
- `docs/superpowers/specs/2026-06-04-cv-master-design.md`: approved design spec.

## Handoff Checklist For Future Agents

Before making changes:

1. Read this file.
2. Read the design spec and roadmap.
3. Check `git status --short`.
4. Preserve user changes. Do not revert files you did not modify.
5. If implementing code, create or update tests for the changed behavior.
6. Run the relevant verification commands before claiming completion.

Before handing off:

1. Update docs if architecture, commands, or environment variables changed.
2. Summarize completed work, verification evidence, and remaining risks.
3. Leave the repository in a state another coding agent can understand quickly.
