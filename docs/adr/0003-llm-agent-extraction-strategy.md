# ADR 0003: LLM Agent Extraction Strategy

> **Status**: Accepted | **Date**: 2026-06-05 | **Supersedes**: Rule-based `_parse_markdown_sections()` in `ingestion.py`

---

## Context

The CV Master product requires extracting structured career data from unstructured user inputs:

1. **Resume files** (Markdown, PDF, TXT): extract positions, skills, education, projects, certifications, achievements, and profile info.
2. **Job descriptions** (pasted text, URL fetch, Markdown upload): extract requirements, skills, seniority, and keywords.
3. **Free-text notes** (future): extract career facts from user-written notes.

The current implementation uses a Python `re.split()` + keyword dictionary approach (`_parse_markdown_sections()` in `apps/api/app/api/routes/ingestion.py`). This works for well-structured Markdown but:

- Cannot handle PDF, DOCX, or unstructured text
- Cannot infer entity types from arbitrary section headers
- Cannot extract structured fields (dates, company names, skill levels) from free text
- Cannot deduplicate or merge overlapping sections
- Has zero confidence estimation
- Requires manual header-to-entity-type mapping maintenance

The product vision includes a user-managed agent interface where extraction rules can be customized. Starting with LLM-based extraction now builds toward that vision.

## Decision

**Use LLM agents with structured output for all entity extraction tasks.** Replace the rule-based `_parse_markdown_sections()` with LLM-powered extraction agents. Apply the same pattern to JD analysis, gap analysis, and future knowledge import flows.

### Core Principles

1. **One agent per extraction domain**. Each extraction task (resume parsing, JD analysis, skill extraction) has its own agent with a dedicated prompt and output schema.
2. **Structured output always**. Every agent response is validated against a Pydantic schema. No free-text parsing of LLM output.
3. **Confidence is explicit**. Every extracted entity carries a confidence level (`high`, `medium`, `low`, `needs_review`).
4. **Evidence grounding is built in**. Extracted entities link to source text spans for traceability.
5. **Human review is mandatory before import**. LLM output goes to the candidate review UI, never directly into the knowledge base.
6. **Provider-agnostic**. All agents use the existing `LLMClient` interface from `app/llm/base.py`. No provider-specific code in agents.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Extraction Pipeline                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input (file/text)                                            │
│       │                                                       │
│       ▼                                                       │
│  ┌──────────────┐                                            │
│  │ Text Extractor│  ← Per-format (PDF→text, MD→text, etc.)   │
│  └──────┬───────┘                                            │
│         │ raw_text                                            │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                    │
│  │        Extraction Orchestrator        │                    │
│  │  (decides which agents to invoke)     │                    │
│  └────────┬─────────┬──────────┬────────┘                    │
│           │         │          │                              │
│           ▼         ▼          ▼                              │
│  ┌──────────┐ ┌────────┐ ┌──────────┐                       │
│  │ Profile  │ │ Career │ │ Skills   │  ...                   │
│  │ Extractor│ │ Extractor│ │ Extractor│                      │
│  └────┬─────┘ └───┬────┘ └────┬─────┘                       │
│       │            │           │                              │
│       ▼            ▼           ▼                              │
│  ┌──────────────────────────────────────┐                    │
│  │      Candidate Snippets (DB)          │                    │
│  │  ResumeIngestionCandidate[]            │                    │
│  └────────────────┬─────────────────────┘                    │
│                   │                                           │
│                   ▼                                           │
│  ┌──────────────────────────────────────┐                    │
│  │        User Review UI                 │                    │
│  │  Accept / Edit / Reject / Merge       │                    │
│  └────────────────┬─────────────────────┘                    │
│                   │                                           │
│                   ▼                                           │
│  ┌──────────────────────────────────────┐                    │
│  │        Import Service                 │                    │
│  │  Creates Position, Skill, etc. rows   │                    │
│  └──────────────────────────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Agent Definitions

### Agent 1: Resume Profile Extractor

**Input**: Raw resume text (up to 8000 chars)
**Output Schema**:
```json
{
  "full_name": "string | null",
  "email": "string | null",
  "phone": "string | null",
  "location": "string | null",
  "headline": "string | null",
  "links": ["string"],
  "summary": "string | null",
  "confidence": "high | medium | low",
  "source_spans": [{"field": "string", "start": 0, "end": 0}]
}
```

### Agent 2: Resume Experience Extractor

**Input**: Raw resume text (up to 8000 chars)
**Output Schema**:
```json
{
  "positions": [{
    "company": "string",
    "title": "string",
    "start_date": "string | null",
    "end_date": "string | null",
    "is_current": false,
    "description": ["string"],
    "tech_stack": ["string"],
    "location": "string | null",
    "confidence": "high | medium | low",
    "source_spans": [{"start": 0, "end": 0}]
  }]
}
```

### Agent 3: Resume Education Extractor

**Input**: Raw resume text
**Output Schema**:
```json
{
  "education": [{
    "institution": "string",
    "degree": "string",
    "field": "string",
    "start_date": "string | null",
    "end_date": "string | null",
    "location": "string | null",
    "confidence": "high | medium | low"
  }]
}
```

### Agent 4: Resume Skills Extractor

**Input**: Raw resume text
**Output Schema**:
```json
{
  "skills": [{
    "name": "string",
    "category": "programming | cloud | database | framework | tool | soft | other",
    "inferred_proficiency": 0-100,
    "years_experience": "number | null",
    "confidence": "high | medium | low"
  }]
}
```

### Agent 5: Resume Projects Extractor

**Input**: Raw resume text
**Output Schema**:
```json
{
  "projects": [{
    "title": "string",
    "role": "string | null",
    "summary": "string",
    "skills": ["string"],
    "tools": ["string"],
    "domain": "string | null",
    "confidence": "high | medium | low"
  }]
}
```

### Agent 6: Resume Certifications Extractor

**Input**: Raw resume text
**Output Schema**:
```json
{
  "certifications": [{
    "name": "string",
    "issuer": "string | null",
    "date": "string | null",
    "confidence": "high | medium | low"
  }]
}
```

### Agent 7: Resume Achievements Extractor

**Input**: Raw resume text
**Output Schema**:
```json
{
  "achievements": [{
    "title": "string",
    "description": "string",
    "metric_name": "string | null",
    "metric_value": "string | null",
    "confidence": "high | medium | low"
  }]
}
```

## Orchestration Strategy

The `ExtractionOrchestrator` receives the raw text and decides which agents to invoke:

**MVP approach (parallel)**: Invoke all 7 agents in parallel. Each agent receives the full text and extracts its domain-specific entities. This is the simplest approach and works well for resumes up to ~8000 tokens.

**Optimized approach (future)**: Use a pre-classification agent to identify which sections exist, then invoke only the relevant extractors. This reduces token usage and latency.

**Agent chaining (future)**: Some extractors can benefit from the output of others (e.g., skills can be cross-referenced with experience descriptions to improve confidence).

For MVP, the parallel approach is sufficient. The `MockLLMClient` already has infrastructure to return structured outputs by schema name.

## Structured Output Enforcement

All agents use the `response_schema` parameter of `LLMClient.generate()`. The schema is passed as a JSON Schema object. The LLM adapter is responsible for enforcing structured output (provider-native structured output or guided generation).

For the MVP using `openai_compatible` (DeepSeek), structured output is achieved via the `response_format` parameter with JSON Schema.

For providers without native structured output support, the adapter falls back to parsing JSON from the completion text.

## Confidence Estimation

Each extracted entity carries a confidence level derived from the LLM's own assessment:

| Confidence | Meaning | UI Treatment |
|---|---|---|
| `high` | Clear, unambiguous extraction with strong signal | Green badge, pre-accepted |
| `medium` | Extracted but some ambiguity | Yellow badge, needs review |
| `low` | Tentative extraction, likely needs editing | Red badge, explicitly review |
| `needs_review` | The agent is uncertain | Amber badge, user must confirm |

Additionally, the orchestrator can apply heuristics:
- Skill with 0 years_experience → downgrade to `low`
- Position with no date range → downgrade to `medium`
- Education with only institution name → downgrade to `medium`

## Consequences

### Positive

- **Handles any format**: PDF, DOCX, Markdown, TXT all normalize to text before extraction
- **Structured extraction from unstructured text**: LLM can identify implicit entities (e.g., skills mentioned in experience paragraphs)
- **Self-assessed confidence**: Users can prioritize review of low-confidence items
- **Extensible**: New extractors can be added without changing existing ones
- **Provider-agnostic**: Works with any LLM provider through the existing adapter pattern
- **Aligned with product vision**: User-manageable agents in the future

### Negative

- **Latency**: LLM calls add 2-5 seconds per extraction (7 parallel calls in MVP ~ 3-5s total)
- **Cost**: Each extraction consumes LLM tokens (~$0.01-0.05 per resume depending on provider)
- **Non-deterministic**: Same input may produce slightly different outputs across runs
- **Requires LLM provider**: Falls back to rule-based if no provider is configured
- **Mock complexity**: Testing requires realistic mock LLM responses

### Mitigations

- **Parallel invocation**: All 7 agents run concurrently, so total latency = slowest agent, not sum
- **Caching**: Extraction results are cached by content hash; re-uploading the same file reuses results
- **Fallback**: If LLM is unavailable, fall back to the existing rule-based parser with degraded quality
- **User review gate**: No entity enters the knowledge base without human approval
- **Mock LLM fixtures**: Pre-built mock responses for all 7 agents enable deterministic testing

---

## Files to Create/Modify

### New files

| File | Purpose |
|------|---------|
| `apps/api/app/agents/extraction/__init__.py` | Package init, re-exports |
| `apps/api/app/agents/extraction/orchestrator.py` | ExtractionOrchestrator — invokes agents in parallel |
| `apps/api/app/agents/extraction/profile_extractor.py` | Agent 1: Profile extraction |
| `apps/api/app/agents/extraction/experience_extractor.py` | Agent 2: Experience extraction |
| `apps/api/app/agents/extraction/education_extractor.py` | Agent 3: Education extraction |
| `apps/api/app/agents/extraction/skills_extractor.py` | Agent 4: Skills extraction |
| `apps/api/app/agents/extraction/projects_extractor.py` | Agent 5: Projects extraction |
| `apps/api/app/agents/extraction/certifications_extractor.py` | Agent 6: Certifications extraction |
| `apps/api/app/agents/extraction/achievements_extractor.py` | Agent 7: Achievements extraction |
| `apps/api/app/agents/prompts/extraction_prompts.py` | All extraction prompt templates (versioned) |
| `apps/api/app/schemas/extraction.py` | Pydantic schemas for all extraction agent outputs |
| `apps/api/tests/test_extraction_agents.py` | Tests for all extraction agents (mock LLM) |

### Modified files

| File | Change |
|------|--------|
| `apps/api/app/api/routes/ingestion.py` | Replace `_parse_markdown_sections()` with `ExtractionOrchestrator` |
| `apps/api/app/llm/mock_adapter.py` | Add mock structured outputs for extraction schemas |
| `apps/api/app/schemas/ingestion.py` | Extend `CandidateResponse.extracted_data` schema |
| `docs/04-agent-workflows.md` | Update ingestion workflow to reflect LLM agents |
