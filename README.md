# CV Master

CV Master is a local-first AI agent for generating job-targeted resumes from a user's career knowledge base. The MVP is designed for a single user, private deployment, and high-quality resume generation across PDF, Markdown, HTML, and Word outputs.

The long-term direction is a specialized personal career assistant, not a generic SaaS product. The architecture therefore prioritizes modular agent workflows, durable personal knowledge, provider-agnostic LLM access, and auditable resume claims.

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

## Development Commands

```bash
# Start all services
docker compose -f docker/docker-compose.yml up --build

# Database migrations
docker compose -f docker/docker-compose.yml exec api alembic upgrade head
docker compose -f docker/docker-compose.yml exec api alembic revision --autogenerate -m "description"

# Backend tests
docker compose -f docker/docker-compose.yml exec api pytest
docker compose -f docker/docker-compose.yml exec api pytest tests/test_health.py
docker compose -f docker/docker-compose.yml exec api pytest -k "test_settings"

# Frontend
docker compose -f docker/docker-compose.yml exec web npm run dev
docker compose -f docker/docker-compose.yml exec web npm run build
docker compose -f docker/docker-compose.yml exec web npm run lint

# Local development (without Docker)
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

cd apps/web
npm install
npm run dev
```
