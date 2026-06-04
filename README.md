# CV Master

CV Master is a local-first resume generation agent for building targeted, ATS-friendly resumes from a personal career knowledge base.

The MVP is designed for a single user. It will let the user manage work history, education, certifications, projects, achievements, skills, and supporting evidence, then generate a tailored resume from a job description in PDF, Markdown, HTML, and Word formats.

The longer-term direction is a specialized personal career assistant agent, similar in spirit to local/private assistant systems, but focused on career memory, job targeting, resume generation, interview preparation, and application workflows.

## Planned Capabilities

- Career profile and timeline management
- Local Markdown career vault
- Structured career fact database
- Hybrid retrieval over projects, achievements, skills, and evidence
- JD parsing and ATS keyword extraction
- Resume strategy generation
- Evidence-backed resume writing
- Resume critique and compliance checks
- Export to PDF, Markdown, HTML, and DOCX
- LLM provider selection through environment configuration
- Docker deployment with Postgres, pgvector, Redis, Adminer, API, worker, and web

## Planned Stack

- Backend: Python, FastAPI, LangGraph, SQLAlchemy, Alembic, Celery, Redis
- Database: Postgres with pgvector
- Frontend: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui
- Search API: Tavily in MVP, behind an extensible provider interface
- LLM providers: OpenAI-compatible APIs, OpenAI, Anthropic, and local Ollama

## Documentation

Start with:

- [AGENTS.md](/Users/xizhang/Documents/Playground/cv_master/AGENTS.md)
- [Product Requirements](/Users/xizhang/Documents/Playground/cv_master/docs/01-product-requirements.md)
- [System Architecture](/Users/xizhang/Documents/Playground/cv_master/docs/02-system-architecture.md)
- [Roadmap](/Users/xizhang/Documents/Playground/cv_master/docs/10-roadmap.md)

## Status

Planning documentation has been created. Application code has not been scaffolded yet.

