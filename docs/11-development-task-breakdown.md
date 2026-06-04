# Development Task Breakdown
## Milestone 1 - Scaffold

Tasks:

1. Create repository layout.
2. Add Docker Compose.
3. Add FastAPI base app.
4. Add Next.js app.
5. Add Postgres, Redis, Adminer services.
6. Add `.env.example`.
7. Add root README commands.

Acceptance:

- `docker compose up --build` starts services.
- `GET /health` returns OK.
- Web homepage loads.

## Milestone 2 - Backend Core

Tasks:

1. Implement Pydantic Settings.
2. Implement logging.
3. Implement DB session.
4. Implement SQLAlchemy base models.
5. Configure Alembic.
6. Add pytest setup.

Acceptance:

- migrations run.
- tests pass.
- health check includes DB status.

## Milestone 3 - Career Data CRUD

Tasks:

1. Implement UserProfile.
2. Implement Position.
3. Implement Project.
4. Implement Achievement.
5. Implement Skill.
6. Implement Education.
7. Implement Certification.
8. Implement Evidence.
9. Implement multi-format text extraction service (PDF, DOCX, MD, TXT).
10. Implement LLM agent extraction pipeline (see ADR 0003 and docs/12-agent-pipeline-design.md):
   10a. Create `app/agents/extraction/` package with base `ExtractionAgent` class.
   10b. Implement 7 domain-specific extraction agents (Profile, Experience, Education, Skills, Projects, Certifications, Achievements).
   10c. Create versioned prompt templates in `app/agents/prompts/extraction_prompts.py`.
   10d. Create Pydantic output schemas in `app/schemas/extraction.py`.
   10e. Implement `ExtractionOrchestrator` — parallel agent invocation with caching.
   10f. Update `POST /api/ingestion/resume/upload` to use orchestrator instead of `_parse_markdown_sections()`.
   10g. Add LLM fallback to rule-based parser when LLM is unavailable.
   10h. Update `MockLLMClient` with extraction schema fixtures for testing.
   10i. Add unit tests for each extraction agent with mock LLM.
   10j. Add integration tests for full extraction pipeline.
   10k. Add golden tests with fixture resumes and expected extraction outputs.
11. Implement candidate snippet review API (list, accept, reject, edit).
12. Implement candidate import into knowledge base (creates structured records, triggers embedding).

Acceptance:

- CRUD endpoints work.
- validation errors are consistent.
- tests cover create/read/update/delete.
- Resume in any supported format (MD, PDF, TXT, DOCX) can be uploaded, LLM-extracted into candidates, reviewed, and imported into the knowledge base.
- Rule-based fallback works when LLM is unavailable.
- Each extraction agent returns structured output matching its Pydantic schema.
- Confidence labels are present and accurate.
- All extraction agents have unit tests with mock LLM.
- Golden tests pass with fixture resumes.

## Milestone 4 - Knowledge Retrieval

Tasks:

1. Implement embedding adapter interface.
2. Store embeddings in pgvector.
3. Implement full-text search columns/indexes.
4. Implement hybrid retrieval scoring.
5. Add retrieval search endpoint.

Acceptance:

- sample JD can retrieve relevant records.
- retrieval response includes score components.

## Milestone 5 - LLM Provider Adapters

Tasks:

1. Implement base LLM adapter.
2. Implement OpenAI-compatible adapter.
3. Implement OpenAI adapter.
4. Implement Anthropic adapter.
5. Implement Ollama adapter.
6. Add mocked adapter for tests.

Acceptance:

- provider selected via `LLM_PROVIDER`.
- `/health/llm` validates configuration without exposing secrets.

## Milestone 6 - Resume Workflow

Tasks:

1. Define workflow state.
2. Add prompt templates.
3. Implement JD analyzer.
4. Implement JD URL fetch endpoint (fetch content from URL, extract plain text, create JobDescription).
5. Implement JD Markdown file upload endpoint.
6. Implement strategy planner.
7. Implement resume writer.
8. Implement ATS reviewer.
9. Implement grounding reviewer.
10. Implement job queue execution.

Acceptance:

- mocked LLM can generate a complete resume version.
- JD can be ingested via paste, URL fetch, and Markdown file upload.
- unsupported claims are flagged.
- user approval required before export.

## Milestone 7 - Export Service

Tasks:

1. Markdown renderer.
2. HTML renderer.
3. PDF renderer.
4. DOCX renderer.
5. Artifact model and storage.
6. Download endpoint.

Acceptance:

- all four formats generated.
- files download correctly.
- filenames are safe.

## Milestone 8 - Frontend MVP

Tasks:

1. App shell and navigation.
2. Dashboard (including quick resume upload action).
3. Career Profile (including PDF resume upload, candidate review, and import flow).
4. Projects.
5. Evidence.
6. JD Analyzer (including URL fetch input and Markdown file upload).
7. Resume Generator.
8. Resume Library.
9. Settings.

Acceptance:

- user can complete end-to-end flow from profile data to resume export.
- user can upload an existing PDF resume, review extracted candidates, and import into knowledge base.
- user can ingest a JD via paste, URL fetch, and Markdown file upload.

## Milestone 9 - QA and Hardening

Tasks:

1. Add golden tests.
2. Add Docker integration test.
3. Add manual QA checklist.
4. Review privacy controls.
5. Add sample data.
6. Polish UI.

Acceptance:

- demo-ready MVP.
