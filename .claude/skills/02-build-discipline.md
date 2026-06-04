# Build Discipline

Use while implementing backend, frontend, database, agent workflow, retrieval, export, or configuration changes. This skill keeps implementation maintainable, scoped, typed, and consistent with the project architecture.

## When to Use

- Writing or modifying application code
- Adding API routes
- Adding services
- Adding database models or migrations
- Implementing LangGraph workflows
- Implementing LLM/search provider adapters
- Implementing frontend pages/components
- Implementing export features
- Changing Docker/configuration

## Required Workflow

1. Follow the plan from Blueprint First.
2. Keep changes minimal and task-focused.
3. Match existing file structure, naming, style, and patterns.
4. Reuse existing services, schemas, components, and utilities where possible.
5. Keep route handlers thin; put business logic in services.
6. Use typed schemas at important boundaries.
7. Add or update tests close to the changed behavior.
8. Update docs when setup, API behavior, architecture, workflow, or user-visible behavior changes.
9. Do not refactor unrelated code.
10. Do not silently change product behavior.

## Backend Rules

- Use FastAPI for API routes.
- Use Pydantic schemas for request/response validation.
- Use SQLAlchemy 2 and Alembic for persistence and migrations.
- Use Postgres + pgvector for structured and semantic career data.
- Use Celery + Redis for long-running work.
- Use the consistent error model defined in the API design doc.
- Long-running resume generation, JD analysis, embedding, and export work must use background jobs.

## Agent Workflow Rules

- Use LangGraph for workflow orchestration.
- Workflows must be explicit graphs, not hidden prompt chains.
- Each node reads and writes typed state.
- Main workflow stages: JD analysis → optional research → retrieval → strategy → drafting → ATS review → grounding review → user review → export.
- Generated bullets must carry evidence IDs where possible.
- Unsupported or weak claims must be flagged.
- Prompts must be versioned and testable.
- Use mock LLM in tests.

## Frontend Rules

- Use Next.js App Router, React, TypeScript, Tailwind CSS, and shadcn/ui.
- Use TanStack Query for server state; Zustand only for local UI state.
- Use React Hook Form + Zod for complex forms.
- UI must include loading, success, error, empty, and confirmation states where applicable.
- Use existing shared components before creating new ones.
- Keep UI polished and consistent.

## Export Rules

- Internal resume representation must be structured JSON.
- Render Markdown, HTML, PDF, and DOCX from approved resume versions only.
- Store generated files only under the configured generated files path.
- Prevent path traversal in file operations.
- Generated files must be clean and ATS-friendly.

## Security / Privacy Rules

- Never log API keys.
- Do not commit `.env`, private generated resumes, or personal evidence files.
- Avoid raw prompt/completion logging unless explicitly configured.
- Make cloud LLM and Tavily network calls explicit to the user.
- Adminer is local development only.
- Do not fabricate career claims.

## Done Criteria

- Implementation matches the planned scope.
- Existing architecture is respected.
- Tests were added or updated for changed behavior.
- Docs were updated where needed.
- No unrelated refactor or scope creep was introduced.

## Common Mistakes

- Scattering provider-specific logic across workflow nodes.
- Adding direct LLM logic inside route handlers.
- Skipping migrations for DB changes.
- Building frontend UI without error/loading/empty states.
- Generating claims without evidence traceability.
- Exporting unapproved resume versions.
- Committing secrets or generated private files.
