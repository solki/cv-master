# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current State

This repository contains **planning documentation only — no application code exists yet**. Read [AGENTS.md](./AGENTS.md) for the full agent handoff guide before implementing anything.

## Project Skills

This repository includes local development workflow skills in `.claude/skills/`. Use them before and during all development work. These skills are local to CV Master and take priority over global skills.

**Standard workflow**: Blueprint First → Build Discipline → Experience QA → Ship Handoff

| Skill | When | File |
|---|---|---|
| Blueprint First | Before any non-trivial task | [01-blueprint-first.md](.claude/skills/01-blueprint-first.md) |
| Build Discipline | During implementation | [02-build-discipline.md](.claude/skills/02-build-discipline.md) |
| Experience QA | After implementation, before handoff | [03-experience-qa.md](.claude/skills/03-experience-qa.md) |
| Ship Handoff | Before committing and responding | [04-ship-handoff.md](.claude/skills/04-ship-handoff.md) |

Start with [.claude/skills/skill-index.md](.claude/skills/skill-index.md) to select the right skills for each task.

## Documentation Map

Start with these documents to understand the product and architecture:

| Document | Purpose |
|---|---|
| [AGENTS.md](./AGENTS.md) | Full implementation guide for coding agents |
| [README.md](./README.md) | Project overview and stack |
| [docs/superpowers/specs/2026-06-04-cv-master-design.md](./docs/superpowers/specs/2026-06-04-cv-master-design.md) | Primary consolidated design spec |
| [docs/01-product-requirements.md](./docs/01-product-requirements.md) | MVP scope and user journeys |
| [docs/02-system-architecture.md](./docs/02-system-architecture.md) | Backend, frontend, and deployment topology |
| [docs/03-data-model.md](./docs/03-data-model.md) | Core entities, relationships, and retrieval model |
| [docs/04-agent-workflows.md](./docs/04-agent-workflows.md) | LangGraph resume generation flow |
| [docs/05-api-design.md](./docs/05-api-design.md) | REST API surface |
| [docs/06-frontend-plan.md](./docs/06-frontend-plan.md) | Screens, state management, component strategy |
| [docs/07-deployment-config.md](./docs/07-deployment-config.md) | Docker Compose, env vars, provider selection |
| [docs/08-security-privacy.md](./docs/08-security-privacy.md) | Local-first privacy, secrets, network call rules |
| [docs/09-testing-quality.md](./docs/09-testing-quality.md) | Test categories and quality gates |
| [docs/10-roadmap.md](./docs/10-roadmap.md) | Phased implementation plan |
| [docs/11-development-task-breakdown.md](./docs/11-development-task-breakdown.md) | Milestone-level task breakdown with acceptance criteria |
| [docs/adr/0001-knowledge-base-architecture.md](./docs/adr/0001-knowledge-base-architecture.md) | Hybrid Postgres + Markdown vault decision |
| [docs/adr/0002-llm-provider-strategy.md](./docs/adr/0002-llm-provider-strategy.md) | Provider adapter pattern |

## Target Tech Stack

- **Backend**: Python, FastAPI, LangGraph, SQLAlchemy 2 (async), Alembic, Pydantic Settings, Celery
- **Data**: Postgres + pgvector + PostgreSQL full-text search
- **Cache/Queue**: Redis (Celery broker and result backend)
- **Frontend**: Next.js App Router, React, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Zustand, React Hook Form + Zod
- **LLMs**: Provider-agnostic adapters (`openai_compatible`, `openai`, `anthropic`, `ollama`), selected via `LLM_PROVIDER` env var
- **Search**: Tavily API behind a `SearchProvider` abstraction
- **Deployment**: Docker Compose (api, web, worker, postgres, redis, adminer)

## Key Architectural Decisions

1. **Hybrid knowledge base** ([ADR 0001](./docs/adr/0001-knowledge-base-architecture.md)): Postgres is the canonical structured fact store. A local Markdown vault serves as the human-readable layer. pgvector handles semantic retrieval. Full-text search handles ATS keyword matching. Do not use a pure Obsidian vault or Mem0-style memory as the primary data layer.

2. **Provider adapters** ([ADR 0002](./docs/adr/0002-llm-provider-strategy.md)): All LLM access goes through a common `LLMClient` interface with `generate()`, `stream()`, and `embed()` methods. Agent workflows must never call provider SDKs directly. Search goes through a `SearchProvider` interface.

3. **Evidence grounding is mandatory**: Every generated resume bullet must carry evidence IDs linking it to stored career facts. The grounding review agent classifies claims as `pass`, `needs_user_confirmation`, `unsupported`, or `contradiction`. Human review is required before export.

4. **LangGraph for workflow orchestration**: The resume generation flow has 8 stages (JD analyze → research → retrieve → strategy → draft → ATS review → grounding → user review → export) with retry loops. LangGraph's explicit state transitions are preferred over chained prompts.

## Suggested Repository Layout (once implementation begins)

```text
apps/
  api/
    app/
      api/          # Route definitions
      agents/       # LangGraph workflows
      core/         # Settings, logging, security
      db/           # Sessions, migrations, repositories
      exports/      # Markdown, HTML, PDF, DOCX rendering
      knowledge/    # Profile storage, vault sync, retrieval, embeddings
      llm/          # Provider adapters
      models/       # SQLAlchemy models
      schemas/      # Pydantic request/response schemas
      search/       # Tavily and future search adapters
      services/     # Business logic
      workers/      # Celery tasks
    alembic/
    tests/
  web/
    app/
    components/
    features/
    lib/
    styles/
    tests/
docs/
docker/
knowledge-vault/
```

## Commands (to establish once code exists)

```bash
# Start all services
docker compose up --build

# Database migrations
docker compose exec api alembic upgrade head
docker compose exec api alembic revision --autogenerate -m "description"

# Backend tests
docker compose exec api pytest                              # all tests
docker compose exec api pytest tests/test_agents.py         # single file
docker compose exec api pytest -k "test_resume_generation"  # by keyword

# Frontend
docker compose exec web npm run dev      # dev server
docker compose exec web npm run build    # production build
docker compose exec web npm run lint     # linting
docker compose exec web npm run test     # tests
```

## Implementation Guardrails

- Keep modules small and explicit. Prefer typed schemas and structured outputs over free-form strings.
- Version prompts and cover them with regression tests against fixture profiles and JDs.
- Separate retrieval, strategy, writing, critique, and export concerns into distinct services.
- Never hard-code provider names in workflow logic.
- The MVP is single-user — do not introduce multi-user SaaS features.
- Do not commit secrets, `.env`, generated private resumes, or personal evidence files.
- Update the relevant doc in `docs/` when architecture, API contracts, or data models change. Record major decisions in `docs/adr/`.

## Git Workflow

- Use focused branches for implementation work (not small doc edits).
- Commit atomically: one commit per coherent milestone (scaffold, data model, API slice, frontend slice, agent workflow, export feature, test improvement).
- Before handoff: run relevant verifications, `git status --short --branch`, commit finished work, and summarize the commit hash, verification evidence, and remaining risks.
