# AGENTS.md

This file is the handoff guide for coding agents working on CV Master. Read it before making changes.

## Project Mission

CV Master is a local-first personal career AI agent. The MVP helps one user maintain a structured career knowledge base and generate job-targeted resumes in PDF, Markdown, HTML, and Word formats.

The system should optimize resumes for ATS and recruiter screening while preserving truthfulness, traceability, and user control. It must not fabricate career claims. Every strong resume claim should be grounded in stored career facts, projects, achievements, metrics, or evidence.

## Current Repository State

As of this documentation pass, the repository contains planning documents only. There is no application code yet.

Start with:

- `README.md`
- `docs/superpowers/specs/2026-06-04-cv-master-design.md`
- `docs/01-product-requirements.md`
- `docs/02-system-architecture.md`
- `docs/03-data-model.md`
- `docs/04-agent-workflows.md`
- `docs/05-api-design.md`
- `docs/06-frontend-plan.md`
- `docs/07-deployment-config.md`
- `docs/08-security-privacy.md`
- `docs/09-testing-quality.md`
- `docs/10-roadmap.md`
- `docs/adr/0001-knowledge-base-architecture.md`
- `docs/adr/0002-llm-provider-strategy.md`

## Git Workflow

Use git to make development reviewable and recoverable.

Before making changes:

1. Run `git status --short --branch`.
2. Read the relevant docs and source files.
3. Preserve user changes. Do not revert files you did not modify.
4. Use a focused branch for implementation work when the task is larger than a small documentation edit.

While working:

- Keep commits atomic and describe the product or technical change clearly.
- Prefer one commit per coherent milestone: scaffold, data model, API slice, frontend slice, agent workflow, export feature, or test improvement.
- Do not commit secrets, `.env`, generated private resumes, or personal evidence files.
- Update docs in the same commit when architecture, commands, API contracts, or environment variables change.

Before handing off:

1. Run the relevant verification commands.
2. Run `git status --short --branch`.
3. Commit finished work unless the user explicitly asks not to.
4. Summarize the commit hash, verification evidence, and remaining risks.

## Required Architectural Direction

Build the MVP as:

- A single-user local/private application.
- A backend API written primarily in Python.
- A modular agent backend that can evolve into a vertical personal career assistant.
- A frontend web app with a polished tool-oriented interface.
- A Docker-based local deployment with Postgres and Adminer.

Use these core technologies unless there is a documented reason to change:

- Backend API: FastAPI.
- Agent orchestration: LangGraph.
- ORM and migrations: SQLAlchemy 2 and Alembic.
- Settings: Pydantic Settings.
- Database: Postgres with pgvector.
- Background jobs: Celery with Redis.
- Frontend: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui.
- Search API: Tavily for MVP, behind an abstraction.
- LLM access: provider adapters selected by `LLM_PROVIDER`.

## LLM Provider Requirements

The system must support at least these provider modes:

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
```

Provider code should be implemented through adapters. Do not scatter provider-specific conditionals across agent workflows.

## Data and Knowledge Principles

Postgres is the source of truth for career facts. Markdown files are a human-readable local knowledge layer, not the canonical database.

The knowledge system should include:

- Structured entities for positions, projects, education, certifications, skills, achievements, evidence, resume versions, and job descriptions.
- Markdown career notes that can be edited and searched.
- Embeddings stored in pgvector.
- PostgreSQL full-text search for ATS keywords and exact phrase matching.
- Evidence IDs linked to generated resume bullets.

Do not design the MVP around a generic chat memory store. Mem0-style memory may be added later as an assistant memory layer, but it should not replace the auditable career fact store.

## Agent Workflow Requirements

The resume generation workflow must include these stages:

1. Job description ingestion and analysis.
2. Retrieval of relevant career facts, projects, skills, and achievements.
3. Resume strategy planning.
4. Section and bullet drafting.
5. ATS keyword and readability review.
6. Truthfulness and evidence grounding review.
7. User review and editable finalization.
8. Export to Markdown, HTML, PDF, and Word.

Human review is required before final export. The agent may suggest stronger wording, but it must flag unsupported or weakly supported claims.

## Security and Privacy Baseline

Career data is sensitive. Implement with a local-first privacy posture:

- Never log API keys.
- Avoid storing raw prompts and model responses unless explicitly configured.
- Mark sensitive data in logs and traces.
- Keep Adminer bound to local development only.
- Add authentication before any non-local deployment.
- Make provider choice explicit to the user because cloud LLM calls send career data and job descriptions to third-party providers.

## Suggested Initial Repository Layout

Use this layout when implementation begins:

```text
apps/
  api/
    app/
      api/
      agents/
      core/
      db/
      exports/
      knowledge/
      llm/
      models/
      schemas/
      search/
      services/
      workers/
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

## Development Commands To Establish

Once code exists, standardize these commands in the root README and package files:

```bash
docker compose up --build
docker compose exec api alembic upgrade head
docker compose exec api pytest
docker compose exec web npm run lint
docker compose exec web npm run test
```

If commands differ, update this file and the README immediately.

## Implementation Guardrails

- Keep modules small and explicit.
- Prefer typed schemas and structured outputs over free-form strings.
- Keep prompts versioned and testable.
- Separate retrieval, strategy, writing, critique, and export services.
- Avoid hard-coding provider names in workflow logic.
- Do not introduce multi-user SaaS features in the MVP unless they support future migration without complicating the current product.
- Do not make generated resume text impossible to trace back to source records.

## Documentation Maintenance

When architecture, data models, API contracts, provider behavior, deployment, or user flows change, update the relevant document in `docs/` during the same change.

Major decisions should be recorded in `docs/adr/`.

## External References

- FastAPI: https://fastapi.tiangolo.com/
- LangGraph: https://docs.langchain.com/oss/python/langgraph
- Next.js App Router: https://nextjs.org/docs/app
- Pydantic Settings: https://pydantic.dev/
- Celery: https://docs.celeryq.dev/en/stable/
- pgvector: https://github.com/pgvector/pgvector
- Adminer: https://www.adminer.org/
- Tavily API: https://docs.tavily.com/
