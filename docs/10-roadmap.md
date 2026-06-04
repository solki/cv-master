# Roadmap

## Phase 0: Planning

Status: current documentation phase.

Deliverables:

- Product requirements.
- Knowledge base strategy.
- Architecture.
- Data model.
- Agent workflow design.
- API design.
- Frontend design.
- Deployment and testing plan.
- Agent handoff guide.

## Phase 1: MVP Foundation

Goal: create a working local application shell.

Deliverables:

- Docker Compose environment.
- FastAPI application.
- Postgres with pgvector.
- Alembic migrations.
- Next.js application shell.
- Settings and provider validation.
- Basic health checks.

## Phase 2: Career Knowledge Base

Goal: store and retrieve user career facts.

Deliverables:

- CRUD APIs and UI for profile, positions, projects, skills, education, certifications, achievements, and evidence.
- Markdown vault sync.
- Embedding generation.
- Hybrid retrieval service.
- Profile completeness indicators.

> **MVP Status (2026-06-04)**: CRUD APIs exist for all entities including positions (`/api/positions`).
> The frontend currently has UI pages for Profile, Projects, Evidence but **not** a standalone Positions page.
> Positions management is planned for a future sprint or integration into the Career Profile page.
> Embedding generation and hybrid retrieval are stubbed — keyword search against entity tables is the current fallback (requires `embeddings` table population via Celery task, not yet wired).

## Phase 3: JD Analysis And Retrieval

Goal: turn job descriptions into structured targeting plans.

Deliverables:

- JD ingestion.
- JD analyzer agent.
- Tavily search provider.
- Profile gap analysis.
- Retrieval preview UI.

## Phase 4: Resume Generation

Goal: generate grounded resume drafts.

Deliverables:

- LangGraph resume generation workflow.
- Resume strategy agent.
- Resume writer agent.
- ATS review agent.
- Grounding review agent.
- Editable Resume Studio UI.

## Phase 5: Export System

Goal: export approved resumes in all required formats.

Deliverables:

- Markdown renderer.
- HTML renderer.
- PDF renderer.
- Word renderer.
- Export history.
- ATS-safe template.

## Phase 6: Quality And Polish

Goal: make the MVP reliable enough for real use.

Deliverables:

- End-to-end tests.
- Export smoke tests.
- Agent regression fixtures.
- UI polish.
- Settings UX.
- Error handling and recovery.

## Phase 7: Personal Career Assistant Evolution

Goal: evolve beyond resume generation into a specialized career assistant.

Potential capabilities:

- Interview preparation.
- Job application tracker.
- Recruiter email drafting.
- Career planning.
- Profile gap coaching.
- Portfolio and case study generation.
- Mem0-style conversational memory.
- Local document ingestion.
- More search providers.
- Remote private deployment.

## Explicit Non-Roadmap For Now

- Billing.
- Public SaaS tenant model.
- Team administration.
- Recruiter-side workflows.
