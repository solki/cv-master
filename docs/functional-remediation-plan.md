# CV Master Functional Remediation Plan

> **Status**: Audit complete | **Date**: 2026-06-04
>
> Based on end-to-end inspection of frontend/backend contract, API path tracing, browser reproduction, and manual flow testing.

---

## 1. Executive Summary

The CV Master application has **fundamental wiring gaps** in the resume generation → version → export pipeline. A resume can be created, but no `ResumeVersion` record is ever produced, so export/download always returns 404. The export ID construction in the frontend uses `resume.id` where the backend expects `version.id`. Additionally, several flows have contract mismatches, hardcoded URLs, missing cache invalidation, and incomplete error handling.

**12 confirmed bugs found. 5 high-priority, 4 medium, 3 low.**

---

## 2. Root Cause Themes

| Theme | Explanation |
|---|---|
| **Missing workflow steps** | The `POST /resumes/{id}/generate` endpoint returns `{status: "queued"}` but never creates a `ResumeVersion`. There is no `POST /resume-versions` creation endpoint. |
| **ID type confusion** | Frontend uses `resume.id` in export URL; backend expects `resume_version.id`. The two are different UUIDs. |
| **Hardcoded URLs** | Library page embeds `http://localhost:8000` directly instead of using `NEXT_PUBLIC_API_URL`. |
| **Fragile string parsing** | Export ID format `export_{version_id}_{format}` is split on `_`, which breaks when version_id or format contains underscores. |
| **Missing cache invalidation** | Resume Generator's `createMutation.onSuccess` clears form state but does not call `queryClient.invalidateQueries`. |
| **Unused types and dead code** | `Position` TypeScript type exists but no corresponding UI page. No component imports `useStore` for `selectedResumeId`. |

---

## 3. Confirmed Bugs

### Bug 1: Export from Resume Library returns 404 ★ CRITICAL

**Symptom**: Clicking "Export" in Resume Library opens a page showing `{"detail":"Resume version not found"}`.

**Reproduction**:
1. Navigate to http://localhost:3000/library
2. Hover over a resume row, click "Export"
3. Observe 404 in new browser tab

**Root Cause (multi-layered)**:
1. **No ResumeVersion ever created**: `POST /api/resumes/{id}/generate` returns `{job_id, resume_id, status: "queued"}` but never inserts a `ResumeVersion` row. The entire `resume_versions` table is empty.
2. **Wrong ID in export URL**: Library page line 54 constructs `export_${r.id}_v1_markdown` where `r.id` is a **Resume** UUID. The export endpoint parses this to extract a **ResumeVersion** UUID. Resume IDs ≠ version IDs.
3. **Fragile export ID parsing**: `exports.py` line 21-27 splits `export_id` on `_` character. If version_id or format contain `_` (e.g., `v1`, `docx_template`), the parsing breaks.
4. **Hardcoded origin**: Library page embeds `http://localhost:8000` as a string literal instead of reading `NEXT_PUBLIC_API_URL`.

**Affected files**:
- `apps/web/app/library/page.tsx` (line 53-55) — wrong ID, hardcoded URL
- `apps/api/app/api/routes/resumes.py` (line 52-61) — generate doesn't create version
- `apps/api/app/api/routes/exports.py` (line 21-27) — fragile ID parsing

**Recommended fix**:
1. Add `POST /api/resume-versions` endpoint that creates a ResumeVersion (or extend generate endpoint to create one)
2. Fix Library page to: fetch `GET /api/resumes/{id}/versions`, get latest version_id, construct correct export URL
3. Fix export ID parsing to use a delimiter not present in UUIDs (e.g., colon `:` or use segment count)
4. Replace hardcoded localhost with `process.env.NEXT_PUBLIC_API_URL`

**Test to add**: `test_export_with_real_version`, `test_library_export_button_uses_version_id`

**Priority**: **CRITICAL** — Blocks core product workflow

---

### Bug 2: Resume Generator does not invalidate query cache ★ HIGH

**Symptom**: After creating a resume, the "Your Resumes" list does not refresh. User must navigate away and back to see the new resume.

**Root Cause**: `createMutation.onSuccess` at `resumes/page.tsx` line 24 only clears form state (`setTitle(""); setTargetRole("");`). It does not call `queryClient.invalidateQueries({ queryKey: ["resumes"] })`.

**Affected files**: `apps/web/app/resumes/page.tsx` (line 24)

**Recommended fix**: Add `queryClient.invalidateQueries({ queryKey: ["resumes"] })` to onSuccess.

**Test to add**: Component test verifying query invalidation after mutation success.

**Priority**: **HIGH** — Confusing UX, appears as data loss

---

### Bug 3: Resume generation pipeline is a stub — no version is produced ★ HIGH

**Symptom**: Clicking "Create Resume" creates a `Resume` record with status "draft", but no `ResumeVersion` is ever created. Export, approve, and version history are all broken because they depend on version records that never exist.

**Root Cause**: `POST /api/resumes/{id}/generate` returns `{job_id, resume_id, status: "queued"}`. The LangGraph workflow is defined (`agents/workflow.py`) but never executed — there is no Celery task wiring or synchronous fallback.

**Affected files**:
- `apps/api/app/api/routes/resumes.py` (line 52-61)
- `apps/api/app/agents/workflow.py` (workflow exists, never called)

**Recommended fix**:
For MVP: Add a synchronous fallback that uses mock LLM to create a minimal `ResumeVersion` with placeholder content. This unblocks export, approve, and library flows. For production: wire the LangGraph workflow via Celery.

**Test to add**: `test_generate_creates_resume_version`, `test_resume_has_version_after_generate`.

**Priority**: **HIGH** — Blocks export, approve, preview flows

---

### Bug 4: Profile form initializes empty, flickers when data loads ★ MEDIUM

**Symptom**: Opening Career Profile page, the form briefly shows empty fields before populating with saved data. If user starts typing during the flicker window, their input is overwritten.

**Root Cause**: `profile/page.tsx` initializes `form` state with empty strings (`useState({ full_name: "", ... })`). When `useQuery` resolves, the form values come from `profile` object read at render time (line 63: `form[field] || (profile as unknown as Record)[field]`), but `form` state isn't synced with the query result.

**Affected files**: `apps/web/app/profile/page.tsx` (line 11, 62-63)

**Recommended fix**: Add `useEffect` that syncs `form` state from `profile` data when it loads: `useEffect(() => { if (profile) setForm({...profile}) }, [profile])`.

**Test to add**: Component test verifying form populates from query data without flicker.

**Priority**: **MEDIUM** — Poor UX, risk of data loss if user edits during load

---

### Bug 5: `links` field in Profile is a single text input but named plural ★ LOW

**Symptom**: The profile `links` field is a single `type="text"` input. Users might try to enter multiple URLs separated by newlines/commas, but the API stores it as a single string. No URL validation.

**Root Cause**: The field is named `links` (plural) suggesting multiple entries, but the backend schema stores it as `String(2000)` — a single string. The frontend renders it as a plain text input with no URL validation.

**Affected files**: `apps/web/app/profile/page.tsx` (line 61), `apps/api/app/models/user_profile.py`, `apps/api/app/schemas/profile.py`

**Recommended fix**: Either rename to `link` (singular) or implement multi-link parsing. Add `type="url"` to input for basic browser validation.

**Priority**: **LOW** — Cosmetic naming issue, no functional breakage

---

### Bug 6: Position TypeScript type defined but no UI page exists ★ MEDIUM

**Symptom**: `lib/types.ts` defines a `Position` interface with all fields (company, title, dates, etc.), and the backend has full CRUD for `/api/positions`, but there is no frontend page to manage positions.

**Root Cause**: Positions were specified in the data model but the frontend implementation only built Projects, Evidence, and Profile pages.

**Affected files**: `apps/web/lib/types.ts` (line 14-19), no corresponding page component

**Recommended fix**: Either add a `/positions` page, integrate positions into the Career Profile as a tab, or explicitly document that MVP omits standalone position management (positions are extracted from PDF resumes).

**Priority**: **MEDIUM** — Data model gap, positions are a core career entity

---

### Bug 7: Resume Library and Resume Generator use different query keys for same endpoint ★ LOW

**Symptom**: Two independent React Query caches exist for the same data — `["resumes"]` and `["library-resumes"]` — both calling `GET /api/resumes`. Updates in one cache don't invalidate the other.

**Root Cause**: `library/page.tsx` uses `queryKey: ["library-resumes"]`, `resumes/page.tsx` uses `queryKey: ["resumes"]`.

**Affected files**: `apps/web/app/library/page.tsx` (line 9), `apps/web/app/resumes/page.tsx` (line 14)

**Recommended fix**: Use consistent query keys. If different params are needed, use `["resumes", { limit: 50 }]` pattern.

**Priority**: **LOW** — Causes stale data when navigating between pages rapidly

---

### Bug 8: Resume Generator create button doesn't show loading spinner ★ LOW

**Symptom**: The "Create Resume" button shows "Creating..." text but no spinner animation (unlike Projects/Evidence save buttons which have `animate-spin`).

**Root Cause**: The button is a simple `<button>` with text toggle. Other pages use the `inline-flex items-center gap-2` pattern with a spinner `<span>`.

**Affected files**: `apps/web/app/resumes/page.tsx` (line 48-51)

**Recommended fix**: Add spinner span matching Projects/Evidence pattern.

**Priority**: **LOW** — Visual consistency

---

### Bug 9: JD Analyzer fetch-url endpoint returns 400 for unreachable URLs — catch misleading ★ HIGH

**Symptom**: Entering `https://example.com/job` in the URL field shows error "Failed to fetch URL: Client error '404 Not Found'". Users may think the app is broken when the actual URL is the problem.

**Root Cause**: The endpoint catches all `httpx` exceptions as 400 with the raw exception message. Real errors (network timeout, DNS failure) and expected errors (URL doesn't exist) are indistinguishable.

**Affected files**: `apps/api/app/api/routes/job_descriptions.py` (line 46-52)

**Recommended fix**: Distinguish between HTTP errors from the target (return 400 with "Target URL returned {status}") and network/timeout errors (return 502 with "Could not reach URL").

**Priority**: **HIGH** — Misleading error messages erode trust

---

### Bug 10: Export ID format `export_{version_id}_{format}` breaks with underscores ★ HIGH

**Symptom**: When `version_id` contains `_` (e.g., if we prepend `v1_` to the ID), the format parsing corrupts the ID.

**Root Cause**: `exports.py` line 21-27 does:
```python
parts = export_id.split("_")
fmt = parts[-1]
version_id = export_id[len("export_"):-len(f"_{fmt}")]
```
If `export_id` = `export_abc_def_ghi_markdown`, then `fmt` = `markdown`, `version_id` = `abc_def_ghi`. But if `fmt` = `v1` and `version_id` = `abc_def`, the parsing is ambiguous.

**Affected files**: `apps/api/app/api/routes/exports.py` (line 21-27), `apps/web/app/library/page.tsx` (line 54)

**Recommended fix**: Use a delimiter not appearing in UUIDs (e.g., `:` or fixed segment count from right):
```python
# Format: export_{version_id}:{format}
parts = export_id.rsplit(":", 1)
# or: fixed segments
segments = export_id.split("_")
fmt = segments[-1]
version_id = "_".join(segments[1:-1])  # "export" is [0]
```
Also add validation that `version_id` matches UUID pattern.

**Priority**: **HIGH** — Data integrity risk

---

### Bug 11: 500 error on profile-gap-analysis with non-existent JD ★ MEDIUM

**Symptom**: `POST /api/retrieval/profile-gap-analysis` with a non-existent `job_description_id` returns 500 "Internal Server Error" instead of 404.

**Root Cause**: The endpoint loads the JD via `crud.get()`. If the JD doesn't exist, `jd` is None. The code may access attributes on None. Also, the JD model's `updated_at` may use `onupdate=func.now()` which triggers SQLAlchemy lazy-load issues similar to Bug C4 in the previous test plan.

**Affected files**: `apps/api/app/api/routes/retrieval.py`

**Recommended fix**: Add explicit None check for JD and return 404. Use `selectinload` or eager loading if lazy attributes cause issues.

**Priority**: **MEDIUM** — Returns 500 instead of helpful 404

---

### Bug 12: Search returns empty results — no embedding generation pipeline ★ MEDIUM

**Symptom**: `POST /api/retrieval/search` always returns `{"results": [], "total": 0}` regardless of query.

**Root Cause**: The `hybrid_search` method tries keyword ILIKE search across entity tables, but the vector similarity path requires `embeddings` table rows. No embedding generation pipeline (Celery task) is wired. The keyword search may also be failing silently.

**Affected files**: `apps/api/app/knowledge/retrieval.py`, `apps/api/app/api/routes/retrieval.py`

**Recommended fix**: Ensure keyword search fallback works correctly for empty vector stores. Log when vector search is unavailable. Add a `POST /api/retrieval/reindex` endpoint to trigger embedding generation.

**Priority**: **MEDIUM** — Core retrieval feature non-functional

---

## 4. API Contract Issues

| # | Issue | Frontend Expects | Backend Provides | Mismatch |
|---|---|---|---|---|
| C1 | Export URL ID type | Uses `resume.id` | Expects `resume_version.id` | Type mismatch — different entities |
| C2 | Export URL format | `export_{resume.id}_v1_{format}` | `export_{version_id}_{format}` | ID source wrong; `v1` is hardcoded |
| C3 | Library API_BASE | `"http://localhost:8000"` hardcoded | Served from `NEXT_PUBLIC_API_URL` | Inconsistent origin |
| C4 | Resume generation response | Expects version to exist after generate | Returns `{status: "queued"}`, creates nothing | Missing workflow step |
| C5 | Query key duplication | `["resumes"]` vs `["library-resumes"]` | Same `GET /api/resumes` | Cache split |

---

## 5. Frontend Routing/Action Issues

| # | Issue | Location |
|---|---|---|
| F1 | No "Generate" action after JD analysis — the CTA link goes to `/resumes` but doesn't pass the JD ID | `jd/page.tsx` — hardcoded `<a href="/resumes">` |
| F2 | Resume list items are read-only — no click action, no edit, no delete, no view versions | `resumes/page.tsx` line 66-75 |
| F3 | `useStore.selectedResumeId` is never set by any component | All pages — no setter call |
| F4 | No loading state on JD dropdown in Resume Generator — shows empty until JDs load | `resumes/page.tsx` line 41-46 |

---

## 6. Missing Tests

| # | Test Needed | Priority |
|---|---|---|
| T1 | `test_resume_generate_creates_version` — verify version row exists after generate | CRITICAL |
| T2 | `test_export_download_with_valid_version` — end-to-end export flow | CRITICAL |
| T3 | `test_library_export_url_uses_version_id` — contract validation | HIGH |
| T4 | `test_resume_list_refreshes_after_create` — cache invalidation | HIGH |
| T5 | `test_gap_analysis_returns_404_for_missing_jd` — error handling | MEDIUM |
| T6 | `test_search_returns_keyword_results` — retrieval fallback | MEDIUM |
| T7 | `test_profile_form_syncs_from_query` — no flicker | MEDIUM |
| T8 | `test_fetch_url_distinguishes_http_errors` — error classification | MEDIUM |
| T9 | Component tests for Resume Generator cache invalidation | HIGH |
| T10 | Component tests for Library export button behavior | HIGH |

---

## 7. Documentation Gaps

| # | Gap | Doc to Update |
|---|---|---|
| D1 | `docs/05-api-design.md` doesn't specify that generate is async/queued, not synchronous | API design doc |
| D2 | `docs/04-agent-workflows.md` describes 8-stage pipeline but implementation is all stubs | Agent workflow doc |
| D3 | `docs/06-frontend-plan.md` doesn't specify export flow contract (version_id vs resume_id) | Frontend plan |
| D4 | No API contract doc showing exact request/response shapes for export download | API design doc |
| D5 | `docs/03-data-model.md` should clarify Resume vs ResumeVersion identity for exports | Data model doc |

---

## 8. Prioritized Remediation Plan

### Phase 1: Unblock the Core Workflow (P0 — ~4hrs)
1. **Add minimal ResumeVersion creation** to `POST /resumes/{id}/generate` — create a version row with placeholder `content_json` (mock resume data). This unblocks export, approve, and library.
2. **Fix export ID construction in Library** — fetch versions, use version_id, use `NEXT_PUBLIC_API_URL`
3. **Fix export ID parsing** — use safe delimiter
4. **Add tests** T1, T2

### Phase 2: Fix User-Visible Bugs (P1 — ~3hrs)
5. **Fix Resume Generator cache invalidation** — add `invalidateQueries`
6. **Fix profile form flicker** — add `useEffect` sync
7. **Fix JD Analyzer error messages** — distinguish HTTP errors
8. **Fix gap-analysis 404** — add explicit None check
9. **Add tests** T3, T4, T5, T9

### Phase 3: Polish and Consistency (P2 — ~2hrs)
10. **Add Resume list actions** — edit, delete, view versions
11. **Unify query keys** — `["resumes"]` across Library and Generator
12. **Fix JD Analyzer CTA** — pass JD ID to Resume Generator via query param
13. **Add spinner to Create Resume button**
14. **Add tests** T6, T7, T8

### Phase 4: Documentation (P3 — ~1hr)
15. Update API design docs with export contract
16. Mark stubbed endpoints in agent workflow doc
17. Add position management to roadmap or explicitly descope

---

## 9. Acceptance Criteria

After remediation:
- [ ] Clicking "Export" in Resume Library downloads a Markdown file (not shows 404)
- [ ] Creating a resume refreshes the list immediately
- [ ] Export URL uses `NEXT_PUBLIC_API_URL`, not hardcoded localhost
- [ ] Profile form shows loaded data without empty-field flicker
- [ ] JD Analyzer shows distinct error messages for "URL not found" vs "network error"
- [ ] `POST /api/resumes/{id}/generate` creates a `ResumeVersion` row
- [ ] Library export button fetches versions before constructing URL
- [ ] All new tests pass
- [ ] Existing 40 tests still pass

---

## 10. Manual QA Checklist

| # | Flow | Steps | Expected |
|---|---|---|---|
| 1 | Resume → Export | Create resume → Generate → Library → Export | Markdown file downloads |
| 2 | Resume list refresh | Create resume → observe list | New resume appears immediately |
| 3 | Profile edit | Open Profile → Edit → Save | No flicker, data persists |
| 4 | JD URL error | Enter `https://httpstat.us/404` → Fetch | Clear "URL returned 404" message |
| 5 | JD URL timeout | Enter `https://10.255.255.1` → Fetch | Clear "Could not reach" message |
| 6 | Upload resume PDF | Profile → Upload `.pdf` | Success message with ingestion ID |
| 7 | Upload JD .md | JD Analyzer → Upload `.md` | Structured output with keywords |
| 8 | Upload invalid file | Profile → Upload `.jpg` | Clear "Unsupported file type" error |
| 9 | Gap analysis missing JD | API call with bad ID | 404, not 500 |
| 10 | Settings health | Navigate to Settings | Green dots visible, status readable |

---

## 11. Automated Test Plan

New test file: `apps/api/tests/test_resume_workflow.py`

```python
class TestResumeVersionCreation:
    async def test_generate_creates_resume_version(self, async_client):
        # Create JD → create resume → generate → verify version exists
        ...

    async def test_export_download_with_version(self, async_client):
        # Full: create resume → generate → get versions → export download
        ...

class TestExportParsing:
    async def test_export_id_with_underscore_version(self, async_client):
        ...

    async def test_invalid_export_id_format(self, async_client):
        ...
```

New test file: `apps/api/tests/test_retrieval.py` (extend existing)

Update: `apps/api/tests/test_uploads.py` (already created, 17 tests)

---

## Appendix A: Files to Change in Remediation

| Phase | File | Change |
|---|---|---|
| P0 | `apps/api/app/api/routes/resumes.py` | Add version creation in generate endpoint |
| P0 | `apps/web/app/library/page.tsx` | Fetch versions, use version_id, use API_BASE |
| P0 | `apps/api/app/api/routes/exports.py` | Fix export ID parsing |
| P1 | `apps/web/app/resumes/page.tsx` | Add cache invalidation, spinner |
| P1 | `apps/web/app/profile/page.tsx` | Add useEffect sync for form |
| P1 | `apps/api/app/api/routes/job_descriptions.py` | Improve fetch-url error classification |
| P1 | `apps/api/app/api/routes/retrieval.py` | Fix gap-analysis 404 |
| P2 | `apps/web/app/jd/page.tsx` | Pass JD ID via query param |
| P3 | `docs/05-api-design.md` | Export contract documentation |
