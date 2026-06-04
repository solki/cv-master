# Roadmap

## Milestone 0: Documentation And Project Skeleton

Status: documentation created.

Deliverables:

- planning docs
- AGENTS.md
- target architecture
- development roadmap

## Milestone 1: Infrastructure Skeleton

Deliverables:

- monorepo structure
- Docker Compose
- FastAPI app
- Next.js app
- Postgres with pgvector
- Redis
- Adminer
- `.env.example`
- health checks

Acceptance:

- `docker compose up --build` starts all services
- API health endpoint works
- Adminer can connect to Postgres

## Milestone 2: Core Career Data

Deliverables:

- SQLAlchemy models
- Alembic migrations
- CRUD APIs
- frontend forms for profile, work experiences, projects, skills, achievements, education, certifications, evidence

Acceptance:

- user can create and edit core career records
- records persist in Postgres
- evidence can link to career entities

## Milestone 3: Knowledge Base And Retrieval

Deliverables:

- Markdown vault sync
- embedding records
- pgvector semantic search
- Postgres full-text search
- hybrid retrieval service

Acceptance:

- user can search career data by JD-like queries
- retrieval returns relevant evidence with source references

## Milestone 4: LLM And Search Providers

Deliverables:

- provider adapters for OpenAI-compatible, OpenAI, Anthropic, and Ollama
- Tavily search adapter
- provider health checks
- structured output retry handling

Acceptance:

- active provider selected by `LLM_PROVIDER`
- provider can be tested from settings or health endpoint

## Milestone 5: Resume Generation MVP

Deliverables:

- JD analyzer
- retrieval planner
- resume strategist
- resume writer
- resume critic
- generation run tracking
- one ATS-safe template

Acceptance:

- user can paste a JD and generate a grounded resume draft
- generation run stores evidence references and critique output

## Milestone 6: Export System

Deliverables:

- Markdown export
- HTML export
- PDF export
- DOCX export
- download endpoints
- frontend preview

Acceptance:

- user can download all requested formats
- PDF and DOCX are professionally formatted

## Milestone 7: Product Polish

Deliverables:

- resume library
- version comparison
- better critique UI
- missing evidence prompts
- sample data and onboarding flow

Acceptance:

- user can use the system repeatedly for different JDs with minimal friction

## Phase 2: Personal Career Assistant

Candidate capabilities:

- conversational career memory
- interview prep agent
- recruiter email drafting
- application tracker
- richer memory graph
- optional local desktop packaging
- optional profile scoping
- extensible career tool registry

