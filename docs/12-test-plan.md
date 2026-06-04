# CV Master Test Plan & Usability Evaluation

> **Document Status**: Live Evaluation — tests executed against running project at http://localhost:3000 / http://localhost:8000

---

## 1. Current State Assessment

### 1.1 Existing Coverage

| Layer | Tests | Status |
|---|---|---|
| Backend unit + integration | 21 tests in 3 files | ✅ Passing |
| Frontend unit/component | 0 | ❌ None |
| E2E | 0 | ❌ None |
| CI/CD pipeline | 0 | ❌ None |

**Existing backend test files:**
- `tests/test_health.py` (3 tests) — health check, LLM health, API docs availability
- `tests/test_settings.py` (10 tests) — provider validation for all 4 providers, search config, CORS, app env
- `tests/test_crud.py` (8 tests) — profile, positions, projects, skills, education, evidence, JD, resume CRUD + 404 + validation error

### 1.2 Coverage Gaps

| Category | Count | Detail |
|---|---|---|
| Untested API endpoints | 25 of 46 | Ingestion (7), resume versions (5), achievements CRUD (5), certifications CRUD (5), JD fetch-url/upload-md/analyze (3), retrieval (2), exports (2) |
| Untested Python modules | 15 | All LLM adapters, retrieval service, embedding service, export renderer, agent workflow, search adapter, CRUD service, Celery app |
| Frontend tests | 0 | No test framework installed |

---

## 2. Test Organization (Recommended Structure)

### 2.1 Backend Test Structure

```text
apps/api/tests/
  conftest.py                              # Extend with mock LLM fixtures
  test_health.py                           # Existing — keep
  test_settings.py                         # Existing — keep
  test_crud.py                             # Existing — keep
  unit/
    test_llm_factory.py                    # Provider selection dispatch
    test_llm_mock_adapter.py               # MockLLMClient behavior
    test_crud_service.py                   # BaseCRUD in isolation
    test_export_renderer.py                # All 4 formats with fixture content
    test_retrieval_service.py              # Keyword search, merge logic
    test_embedding_service.py              # Embed with mock LLM
    test_search_adapter.py                 # TavilySearchProvider with mocked HTTP
    test_prompts.py                        # Template format validation
  integration/
    test_career_entities.py                # Full CRUD for all 7 entity types
    test_job_descriptions.py               # CRUD + fetch-url + upload-md + analyze
    test_resumes.py                        # CRUD + generate + versions + approve
    test_ingestion.py                      # All 7 ingestion endpoints
    test_retrieval_api.py                  # Search + gap-analysis
    test_exports_api.py                    # Status + download all 4 formats
  workflow/
    test_resume_workflow.py                # Full 7-stage graph with mock LLM
  golden/
    test_resume_output_structure.py        # Structural assertions on generated resumes
    test_export_outputs.py                 # Verify rendered MD/HTML/PDF/DOCX content
```

### 2.2 Frontend Test Structure

```text
apps/web/
  vitest.config.ts                         # NEW: Vitest configuration
  __tests__/
    setup.ts                               # Test setup, mock providers
    unit/
      api.test.ts                          # apiFetch, methods, error handling
      store.test.ts                        # Zustand store actions
    components/
      Dashboard.test.tsx                   # Loading, empty, data states
      CareerProfile.test.tsx               # Edit/save, PDF upload
      Projects.test.tsx                    # List, create form
      Evidence.test.tsx                    # List, create form, type selector
      JDAnalyzer.test.tsx                  # Paste, URL fetch, MD upload
      ResumeGenerator.test.tsx             # Create form, list
      ResumeLibrary.test.tsx               # Table display
      Settings.test.tsx                    # Health display
    e2e/
      full-flow.spec.ts                    # Playwright: full user journey
```

---

## 3. Priority-Ordered Implementation Phases

### Phase P0: Critical Path (Backend Core Features)

| Step | File(s) | Description | Est. |
|---|---|---|---|
| 1 | `conftest.py` | Add MockLLM fixture + app override | 30m |
| 2 | `unit/test_export_renderer.py` | All 4 export formats + fallbacks | 1h |
| 3 | `integration/test_resumes.py` | Resume versions, approve, exports | 1.5h |
| 4 | `integration/test_ingestion.py` | All 7 ingestion endpoints | 1.5h |
| 5 | `integration/test_job_descriptions.py` | fetch-url, upload-md, analyze | 1h |

### Phase P1: Agent Workflow & Retrieval

| Step | File(s) | Description | Est. |
|---|---|---|---|
| 6 | `unit/test_llm_mock_adapter.py` | Mock generate/stream/embed | 1h |
| 7 | `workflow/test_resume_workflow.py` | All 7 nodes + graph | 2h |
| 8 | `unit/test_retrieval_service.py` | Keyword, vector, merge | 1h |
| 9 | `golden/test_resume_output_structure.py` | Fixture-based regression | 1.5h |

### Phase P2: Remaining Backend Coverage

| Step | File(s) | Description | Est. |
|---|---|---|---|
| 10 | `integration/test_career_entities.py` | Achievements + certifications CRUD | 1h |
| 11-13 | Multiple unit files | Embedding, search, prompts, factory | 2.5h |

### Phase P3: Frontend Test Infrastructure

| Step | Description | Est. |
|---|---|---|
| 14 | Install vitest, @testing-library/react, jsdom, @playwright/test | 30m |
| 15 | Create vitest.config.ts + setup.ts | 30m |
| 16 | Write api.ts + store.ts unit tests | 1h |

### Phase P4: Frontend Component Tests

| Step | Description | Est. |
|---|---|---|
| 17 | Page-level tests for all 9 pages | 4h |

### Phase P5: E2E & CI/CD

| Step | Description | Est. |
|---|---|---|
| 18 | Playwright E2E: full user journey, JD flow, export flow | 3h |
| 19 | GitHub Actions: test.yml + lint.yml | 1h |

**Total Estimated Effort**: ~28 hours

---

## 4. Specific Test Cases

### 4.1 Export Renderer Unit Tests

```
test_render_markdown_produces_expected_sections
  Given: fixture content with header, summary, skills, experience, projects, education, certifications
  Then: output contains "# Jane Smith", "## Summary", "## Skills", "## Experience", "## Projects"

test_render_html_wraps_with_doctype
  Given: fixture content
  Then: output starts with "<!DOCTYPE html>" and contains "<title>Jane Smith</title>"

test_render_pdf_falls_back_without_weasyprint
  Mock: ImportError for 'weasyprint'
  Then: returns utf-8 encoded bytes of HTML

test_render_docx_produces_binary
  Given: fixture content with paragraphs and bullet lists
  Then: returns non-empty bytes

test_render_docx_falls_back_without_docx_lib
  Mock: ImportError for 'docx'
  Then: returns utf-8 encoded bytes of markdown
```

### 4.2 Agent Workflow Tests (Mock LLM)

```
test_full_workflow_executes_all_stages
  Given: fixture JD text, MockLLMClient with structured responses
  When: run_resume_generation() is called
  Then: state has all 8 stage keys populated

test_should_revise_when_grounding_finds_unsupported
  Given: grounding_review with unsupported_count=1
  Then: should_revise(state) returns "draft"

test_should_not_revise_when_grounding_passes
  Given: grounding_review with unsupported_count=0, confirmation_required=[]
  Then: should_revise(state) returns "user_review"

test_errors_accumulate_across_nodes
  Mock: two nodes raise exceptions
  Then: state["errors"].length == 2
```

### 4.3 MockLLM Adapter Tests

```
test_mock_generate_returns_structured_for_jd_analysis
  Given: schema={"name": "jd_analysis"}
  Then: returns dict with "job_title": "Software Engineer"

test_mock_generate_returns_plain_for_unknown_schema
  Given: schema={"name": "unknown"}
  Then: returns {"result": "mock_structured_output"}

test_mock_stream_yields_tokens
test_mock_embed_returns_1536_dimensions
test_mock_call_history_records_all
```

### 4.4 Ingestion API Tests

```
test_upload_pdf_accepted        → POST /api/ingestion/resume/upload .pdf → 202
test_upload_rejects_non_pdf     → POST with .txt → 400
test_get_ingestion_status       → GET /api/ingestion/resume/{id} → 200
test_list_candidates_empty      → GET /.../candidates → 200, []
test_accept_candidate           → POST accept → 200, status="accepted"
test_reject_candidate           → POST reject → 200, status="rejected"
test_edit_candidate             → PUT with update → 200
test_import_accepted_candidates → POST import → 200, with counts
```

### 4.5 Resume Version & Export Tests

```
test_list_versions              → GET /api/resumes/{id}/versions → 200, array
test_approve_version            → POST approve → 200
test_request_export             → POST exports → 200, {export_id, status}
test_download_markdown          → GET download → 200, text/markdown
test_download_html              → GET download → 200, text/html
test_download_pdf               → GET download → 200, application/pdf
test_download_docx              → GET download → 200, application/...docx
```

### 4.6 Frontend Component Test Cases (Representative)

```
JD Analyzer:
  test_renders_three_input_methods → "Paste", "Fetch from URL", "Upload" visible
  test_paste_jd_shows_result       → mock api.post, verify JSON preview
  test_fetch_url_shows_error       → mock rejection, verify red error div
  test_loading_state_disables_buttons → "Processing..." shown, buttons disabled

Dashboard:
  test_renders_profile_when_loaded → full_name visible
  test_renders_empty_resume_msg    → "No resumes yet" visible
  test_quick_action_cards_have_links → href="/jd", "/profile", "/resumes"

Career Profile:
  test_edit_toggles_form           → click Edit, fields become editable
  test_save_persists               → mock api.put, verify success
  test_pdf_upload_triggers         → file input triggers api.uploadFile
```

---

## 5. Usability Evaluation Framework

### 5.1 Nielsen's 10 Heuristics

| # | Heuristic | Focus |
|---|-----------|-------|
| H1 | Visibility of system status | Loading indicators, progress feedback |
| H2 | Match between system and real world | Language, mental model alignment |
| H3 | User control and freedom | Cancel, undo, back navigation |
| H4 | Consistency and standards | Navigation, button styles, form layouts |
| H5 | Error prevention | Input validation, constraints, confirmations |
| H6 | Recognition rather than recall | Visible options, contextual help |
| H7 | Flexibility and efficiency of use | Shortcuts, batch operations |
| H8 | Aesthetic and minimalist design | Visual clarity, whitespace |
| H9 | Help users recover from errors | Error messages, recovery paths |
| H10 | Help and documentation | Onboarding, inline help, tooltips |

**Severity Scale:**
- 0 = No issue
- 1 = Cosmetic (fix not urgent)
- 2 = Minor (should fix)
- 3 = Major (important to fix)
- 4 = Catastrophic (must fix immediately)

### 5.2 Per-Page Heuristic Evaluation Target

Each page is evaluated against all 10 heuristics. Below are the pre-identified concerns based on code analysis — these are validated during live testing.

| Page | Key Heuristic Concerns |
|---|---|
| Dashboard | H1 (loading states), H8 (layout clarity) |
| Career Profile | H1 (upload feedback), H3 (edit/cancel), H9 (alert() for errors) |
| Projects | H1 (mutation loading), H5 (form validation), H3 (cancel) |
| Evidence | H1 (loading), H5 (validation) |
| JD Analyzer | H1 (processing state), H3 (cancel in-flight), H9 (error display) |
| Resume Generator | H1 (mutation feedback), H5 (validation) |
| Resume Library | H1 (loading), H7 (row actions) |
| Settings | H1 (status display), H4 (consistency) |
| Knowledge Vault | Static page — minimal interaction concerns |

### 5.3 Navigation & Layout Audit Checklist

| # | Check | Method |
|---|-------|--------|
| N1 | Active nav highlighting | Visual: current page highlighted in sidebar |
| N2 | All 9 nav links work | Click each, verify URL and heading |
| N3 | Mobile responsiveness | Resize to 375px, 768px, 1280px |
| N4 | Sidebar toggle | Check for hamburger menu on mobile |
| N5 | Browser back/forward | Navigate, use back button |
| N6 | Direct URL access | Type /jd directly, verify loads |

---

## 6. Manual Usability Test Protocol

### 6.1 Task-Based Test Script

For each task, record: completion (✓/✗), time on task, errors made, subjective difficulty (1-5).

| # | Task | Page |
|---|------|------|
| T1 | Fill in your career profile (name, headline, location, email) | Profile |
| T2 | Add a past project with title, organization, role, skills | Projects |
| T3 | Add an evidence record (type "metric", title, description) | Evidence |
| T4 | Paste a job description and analyze it | JD Analyzer |
| T5 | Create a new resume targeting a specific role | Resume Generator |
| T6 | Find a previously created resume in the library | Resume Library |
| T7 | Check that the system is properly configured | Settings |
| T8 | Understand what the Knowledge Vault is | Vault |
| T9 | Navigate from Dashboard to Resumes and back to Dashboard | Navigation |
| T10 | Upload a PDF resume for ingestion | Profile |

### 6.2 CSS & Accessibility Checks

- Viewport widths: 375px (mobile), 768px (tablet), 1280px (desktop)
- Browser zoom: 100%, 150%, 200%
- Keyboard navigation: Tab, Enter, Escape
- Screen reader: basic structure check

---

## 7. Live Test Results

> **Test Date**: 2026-06-04
> **Environment**: Docker Compose — api (port 8000), web (port 3000), postgres (pgvector/pg16), redis (7-alpine), adminer (port 8080)

### 7.1 Backend API Smoke Tests

**Test Execution**: 2026-06-04 against running Docker services. Full test suite ran with curl + jq validation.

**Results Summary: 26 passed, 0 failed**

> Note: Initial run exposed two infrastructure issues — missing database migrations and pgvector extension not enabled. Both were resolved during testing (see 7.1.2).

#### 7.1.1 Detailed Results

| # | Endpoint | Method | HTTP | Result |
|---|---|---|---|---|
| 1 | `/health` | GET | 200 | ✅ `{"status":"ok","database":{"status":"ok"}}` |
| 2 | `/health/llm` | GET | 200 | ✅ Provider + search status returned |
| 3 | `/api/profile` | GET | 200 | ✅ Returns profile with id, full_name, headline |
| 4 | `/api/profile` | PUT | 200 | ✅ Updates and returns profile |
| 5 | `/api/positions` | POST | 201 | ✅ Creates position with UUID |
| 6 | `/api/positions/{id}` | DELETE | 204 | ✅ Deletes (204 No Content is correct) |
| 7 | `/api/projects` | POST | 201 | ✅ Creates project |
| 8 | `/api/projects/{id}` | DELETE | 204 | ✅ Deletes |
| 9 | `/api/skills` | POST | 201 | ✅ Creates skill (note: proficiency is 1-5 scale) |
| 10 | `/api/skills/{id}` | DELETE | 204 | ✅ Deletes |
| 11 | `/api/achievements` | POST | 201 | ✅ Creates achievement |
| 12 | `/api/achievements/{id}` | DELETE | 204 | ✅ Deletes |
| 13 | `/api/certifications` | POST | 201 | ✅ Creates certification |
| 14 | `/api/certifications/{id}` | DELETE | 204 | ✅ Deletes |
| 15 | `/api/education` | POST | 201 | ✅ Creates education record |
| 16 | `/api/education/{id}` | DELETE | 204 | ✅ Deletes |
| 17 | `/api/evidence` | POST | 201 | ✅ Creates evidence |
| 18 | `/api/evidence/{id}` | DELETE | 204 | ✅ Deletes |
| 19 | `/api/job-descriptions` | POST | 201 | ✅ Creates JD |
| 20 | `/api/job-descriptions` | GET | 200 | ✅ Lists JDs with pagination |
| 21 | `/api/job-descriptions/{id}/analyze` | POST | 200 | ✅ Returns `{job_id, status: "queued"}` |
| 22 | `/api/job-descriptions/fetch-url` | POST | 400 | ✅ Correctly rejects unreachable URL |
| 23 | `/api/resumes` | POST | 201 | ✅ Creates resume |
| 24 | `/api/resumes` | GET | 200 | ✅ Lists resumes |
| 25 | `/api/resumes/{id}/generate` | POST | 200 | ✅ Returns `{job_id, resume_id, status: "queued"}` |
| 26 | `/api/resumes/{id}/versions` | GET | 200 | ✅ Returns empty versions array |
| 27 | `/api/retrieval/search` | POST | 200 | ✅ Returns `{query, results, total}` |
| 28 | `/api/positions/{uuid}` | GET | 404 | ✅ Correct 404 for nonexistent |

#### 7.1.2 Infrastructure Issues Found & Resolved

| Issue | Root Cause | Fix |
|---|---|---|
| All CRUD endpoints returned 500 | Tables not created — Alembic migration was empty | Added `import app.models` to `env.py`, regenerated migration |
| Migration used `VECTOR` type, failed | `pgvector` extension not enabled in Postgres | Ran `CREATE EXTENSION IF NOT EXISTS vector` |
| First migration was empty `upgrade()` | Models not imported in `env.py`, so `Base.metadata` was empty | Fixed `env.py` to import models before `Base.metadata` reference |

### 7.2 Frontend Usability Evaluation

**Evaluation Method**: Playwright browser automation, Nielsen's 10 heuristics, manual interaction testing.

**All 9 pages loaded successfully** with live data from API. Dashboard displayed Jane Smith's profile and Jane CV resume from smoke test data.

#### 7.2.1 Per-Page Evaluation

**Dashboard (`/`)**
- ✅ Quick action cards (3) render and link correctly
- ✅ Profile overview shows live data (name, headline, location)
- ✅ Recent resumes list shows created resume with status badge
- ⚠️ H1: No loading spinner, just text "Loading profile..." — Severity 1
- ⚠️ H7: No data refresh button — Severity 1

**Career Profile (`/profile`)**
- ✅ View mode shows all fields with "Not set" for empty values
- ✅ Edit button toggles to form with pre-filled values
- ✅ Save Profile persists to API and refreshes view
- ✅ PDF upload section with file input present
- ⚠️ H9: Upload errors use browser `alert()` — Severity 3
- ⚠️ H4: "Cancel" button changes to "Edit" text — functional but inconsistent pattern — Severity 1

**Projects (`/projects`)**
- ✅ "New Project" opens form with grid layout
- ✅ Form fields: title, organization, role, domain, skills, tools, summary
- ✅ Cancel button closes form
- ⚠️ H5: No client-side validation — can submit with empty title — Severity 2
- ⚠️ H1: No loading spinner on save mutation — Severity 2

**Evidence (`/evidence`)**
- ✅ "Add Evidence" toggles form
- ✅ Type dropdown has 6 options (user_statement, document, portfolio_link, metric, manager_feedback, public_artifact)
- ✅ Confidence badge shows percentage with color coding
- ⚠️ Same H1/H5 issues as Projects — Severity 2

**JD Analyzer (`/jd`)**
- ✅ Three input methods: Paste (textarea), URL fetch, MD upload
- ✅ "Analyze JD" sends text to API and displays JSON result
- ✅ URL fetch correctly shows error for unreachable URL (red banner)
- ✅ Buttons disable during loading, show "Processing..."
- ⚠️ H3: No way to cancel in-flight request — Severity 2
- ⚠️ H8: JSON result displayed raw in `<pre>` — formatting for readability would improve UX — Severity 1

**Resume Generator (`/resumes`)**
- ✅ "Create Resume" form with title, target role, JD dropdown
- ✅ JD dropdown populates from API
- ✅ Resume list shows created resumes with status badges
- ✅ "Creating..." shown during mutation
- ⚠️ H5: No validation on required fields — Severity 2

**Resume Library (`/library`)**
- ✅ Table with Title, Target Role, Status, Date columns
- ✅ Status color-coded (green = approved, yellow = draft)
- ✅ Empty state: "No resumes in library yet."
- ⚠️ H7: No row actions (click to view, export, delete) — Severity 2

**Knowledge Vault (`/vault`)**
- ✅ Static content: 8 vault paths with descriptions
- ✅ Frontmatter ID sync note displayed
- ✅ Clean layout, good information hierarchy
- ✅ No issues — purely informational page

**Settings (`/settings`)**
- ✅ System Health card with green indicator (status: healthy, database: connected)
- ✅ LLM Provider card with yellow indicator (provider: openai_compatible, search: not configured)
- ✅ Configuration instructions for env vars
- ✅ Live data from `/health` and `/health/llm` endpoints
- ⚠️ H6: "N/A" shown briefly while loading — could use skeleton — Severity 1

#### 7.2.2 Navigation & Layout Audit

| # | Check | Result |
|---|---|---|
| N1 | Active nav highlighting | ❌ **Failed** — No visual indication of current page |
| N2 | All 9 nav links work | ✅ Passed — Each navigates to correct page |
| N3 | Mobile (375px) | ⚠️ Sidebar hidden (`hidden md:flex`), no hamburger menu |
| N4 | Desktop (1280px) | ✅ Full sidebar + content layout works |
| N5 | Browser back/forward | ⚠️ Works, but no loading state management |
| N6 | Direct URL access | ✅ All routes load correctly when accessed directly |

#### 7.2.3 Mobile Responsiveness

At 375px viewport:
- Sidebar disappears entirely (correct per `hidden md:flex`)
- **No hamburger menu or alternative navigation** — user is stranded with no way to navigate between pages
- Content fills full width, readable
- This is a Severity 3 issue for mobile users

### 7.3 Screenshot Evidence

All screenshots captured at 1280×900 (desktop) and 375×812 (mobile):

| File | Page | State |
|---|---|---|
| [01-dashboard.png](screenshots/01-dashboard.png) | Dashboard | Live data: Jane Smith profile, Jane CV resume |
| [02-career-profile.png](screenshots/02-career-profile.png) | Career Profile | View mode with profile data |
| [02b-profile-edit-mode.png](screenshots/02b-profile-edit-mode.png) | Career Profile | Edit mode with form fields |
| [03-projects.png](screenshots/03-projects.png) | Projects | New project form open |
| [04-evidence.png](screenshots/04-evidence.png) | Evidence | Empty state |
| [05-jd-analyzer.png](screenshots/05-jd-analyzer.png) | JD Analyzer | Three input methods visible |
| [06-resume-generator.png](screenshots/06-resume-generator.png) | Resume Generator | Create form + resume list |
| [07-resume-library.png](screenshots/07-resume-library.png) | Resume Library | Table with resume data |
| [08-vault.png](screenshots/08-vault.png) | Knowledge Vault | Static vault structure |
| [09-settings.png](screenshots/09-settings.png) | Settings | Health + LLM status cards |
| [10-mobile-dashboard.png](screenshots/10-mobile-dashboard.png) | Dashboard (375px) | Mobile layout — no sidebar |

---

## 8. Quick-Start: API Smoke Test Commands

```bash
# Health checks
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8000/health/llm | jq .

# Profile
curl -s http://localhost:8000/api/profile | jq .
curl -s -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Jane Smith","headline":"Senior Engineer","location":"San Francisco"}' | jq .

# Career entities
curl -s -X POST http://localhost:8000/api/positions \
  -H "Content-Type: application/json" \
  -d '{"company":"Acme Corp","title":"Senior Developer"}' | jq .

curl -s -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"title":"Data Pipeline","organization":"Acme","role":"Tech Lead","summary":"Built ETL pipeline"}' | jq .

curl -s -X POST http://localhost:8000/api/skills \
  -H "Content-Type: application/json" \
  -d '{"name":"Python","category":"Programming","proficiency":90}' | jq .

curl -s -X POST http://localhost:8000/api/achievements \
  -H "Content-Type: application/json" \
  -d '{"title":"Revenue Growth","description":"Grew revenue 20%"}' | jq .

curl -s -X POST http://localhost:8000/api/certifications \
  -H "Content-Type: application/json" \
  -d '{"name":"AWS Solutions Architect","issuer":"Amazon"}' | jq .

curl -s -X POST http://localhost:8000/api/education \
  -H "Content-Type: application/json" \
  -d '{"institution":"MIT","degree":"BSc","field":"Computer Science"}' | jq .

curl -s -X POST http://localhost:8000/api/evidence \
  -H "Content-Type: application/json" \
  -d '{"title":"Performance Review","type":"document","confidence":1.0}' | jq .

# JD operations
curl -s -X POST http://localhost:8000/api/job-descriptions \
  -H "Content-Type: application/json" \
  -d '{"title":"Backend Engineer","company":"TechCo","raw_text":"Looking for a Python developer with 5+ years experience in FastAPI and PostgreSQL."}' | jq .

curl -s -X POST http://localhost:8000/api/job-descriptions/fetch-url \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/job"}' | jq .

# Resume
curl -s -X POST http://localhost:8000/api/resumes \
  -H "Content-Type: application/json" \
  -d '{"title":"Jane - Backend CV","target_role":"Senior Backend Engineer"}' | jq .

# Retrieval
curl -s -X POST http://localhost:8000/api/retrieval/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Python developer","top_k":5}' | jq .

curl -s -X POST http://localhost:8000/api/retrieval/profile-gap-analysis \
  -H "Content-Type: application/json" \
  -d '{"job_description_id":"any-id"}' | jq .
```

---

## Appendix A: Nielsen Heuristic Evaluation Sheet (Per Page)

| Page | H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | H9 | H10 | Total Issues |
|------|----|----|----|----|----|----|----|----|----|-----|-------------|
| Dashboard | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 2 |
| Career Profile | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 3 | 0 | 5 |
| Projects | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 4 |
| Evidence | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 4 |
| JD Analyzer | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 3 |
| Resume Generator | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 3 |
| Resume Library | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 3 |
| Settings | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2 |
| Knowledge Vault | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **9** | **0** | **2** | **1** | **6** | **1** | **3** | **1** | **3** | **0** | **26** |

## Appendix B: Recommended UI Fixes (Prioritized)

| # | Issue | Severity | Page(s) | Recommendation |
|---|-------|----------|---------|----------------|
| 1 | No active nav highlighting | 3 | All | Use `usePathname()` from next/navigation in layout.tsx |
| 2 | No ErrorBoundary | 3 | All | Create `<ErrorBoundary>` component wrapping pages |
| 3 | `alert()` for errors | 3 | Profile | Replace with toast notification component |
| 4 | No form validation | 2 | Projects, Evidence | Wire up react-hook-form + zod schemas |
| 5 | No mutation loading spinners | 2 | All | Add spinner animation inside submit buttons |
| 6 | Missing delete/edit UI | 2 | Library, Projects | Add action buttons to rows |
| 7 | Zustand store unused | 1 | All | Either use sidebarOpen for nav toggle or remove |
| 8 | No mobile nav | 2 | All | Add hamburger menu for < md breakpoint |
| 9 | No query error surfacing | 2 | Most pages | Check `isError` from useQuery, display inline error |
| 10 | Unused dependencies | 1 | — | Either implement react-hook-form/zod or remove from package.json |
