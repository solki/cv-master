# Agent Pipeline Design — LLM Extraction & Analysis

> **Status**: Design | **Date**: 2026-06-05 | **Depends on**: ADR 0003

---

## 1. Overview

This document defines the LLM agent pipeline architecture for extracting structured career data from unstructured inputs (resume files, job descriptions, free-text notes). It extends the extraction strategy defined in [ADR 0003](adr/0003-llm-agent-extraction-strategy.md) with implementation-level detail.

## 2. Agent Lifecycle

Every extraction agent follows the same lifecycle:

```
┌─────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│ Input   │───▶│ Prompt    │───▶│ LLM Call │───▶│ Schema    │───▶│ Output   │
│ (text)  │    │ Assembly  │    │ generate │    │ Validation│    │ (Pydantic)│
└─────────┘    └───────────┘    └──────────┘    └───────────┘    └──────────┘
     │                                                               │
     │              ┌──────────┐                                     │
     └─────────────▶│  Cache   │◀────────────────────────────────────┘
                    │ (by hash)│
                    └──────────┘
```

### 2.1 Input

- `raw_text: str` — the normalized text content (PDF text, Markdown, TXT)
- `context: dict | None` — optional context from other extractors
- `max_chars: int = 8000` — truncation limit to control token usage

### 2.2 Prompt Assembly

Each agent has a versioned prompt template with:
- **System message**: role description and extraction rules
- **User message**: the raw text to analyze
- **Output format instruction**: JSON Schema for structured output

Prompts are stored in `apps/api/app/agents/prompts/extraction_prompts.py` with version numbers for regression testing.

### 2.3 LLM Call

```python
result = await llm_client.generate(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    response_schema=output_schema,  # JSON Schema for structured output
    temperature=0.1,                # Low temperature for extraction
    max_tokens=2000,                # Limit response size
)
```

### 2.4 Schema Validation

```python
from app.schemas.extraction import ProfileExtractionResult

validated = ProfileExtractionResult.model_validate(result)
# Raises ValidationError if LLM output doesn't match schema
```

### 2.5 Output

Returns a Pydantic model instance. The orchestrator maps these to `ResumeIngestionCandidate` records.

### 2.6 Caching

Results are cached by `sha256(raw_text + agent_name)`. Re-uploading the same file (with the same content) returns cached results. Cache TTL: 24 hours (configurable).

## 3. Extraction Orchestrator

```python
class ExtractionOrchestrator:
    """Orchestrates parallel LLM extraction agents."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.agents = [
            ProfileExtractor(llm_client),
            ExperienceExtractor(llm_client),
            EducationExtractor(llm_client),
            SkillsExtractor(llm_client),
            ProjectsExtractor(llm_client),
            CertificationsExtractor(llm_client),
            AchievementsExtractor(llm_client),
        ]

    async def extract_all(self, raw_text: str) -> list[ExtractionResult]:
        """Run all extractors in parallel. Returns merged results."""
        tasks = [agent.extract(raw_text) for agent in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        merged = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Extractor {self.agents[i].name} failed: {result}")
                continue
            merged.extend(result.to_candidates())
        return merged

    async def extract_single(self, raw_text: str, domain: str) -> ExtractionResult:
        """Run a single extractor by domain name."""
        agent = next((a for a in self.agents if a.name == domain), None)
        if agent is None:
            raise ValueError(f"Unknown extraction domain: {domain}")
        return await agent.extract(raw_text)
```

### 3.1 Integration with Upload Endpoint

```python
@router.post("/resume/upload", status_code=202)
async def upload_resume(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # ... validation, file reading ...

    # Create ingestion record
    ingestion = await ingestion_crud.create(db, ResumeIngestionCreate(
        source_filename=file.filename, status="processing"
    ))

    # Try LLM extraction
    try:
        llm = get_llm_client()
        orchestrator = ExtractionOrchestrator(llm)
        candidates = await orchestrator.extract_all(raw_text)

        # Create candidate records
        for c in candidates:
            db.add(ResumeIngestionCandidate(
                resume_ingestion_id=ingestion.id,
                entity_type=c.entity_type,
                extracted_data=c.model_dump(),
                confidence=c.confidence,
                status="pending",
            ))

        ingestion.status = "parsed"
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        ingestion.status = "parsed"  # Still mark as parsed
        # In fallback: use rule-based _parse_markdown_sections()

    await db.flush()
    return ResumeUploadResponse(ingestion_id=ingestion.id, status=ingestion.status)
```

## 4. Agent Prompt Design

### 4.1 Prompt Template Structure

All extraction prompts follow this structure:

```
SYSTEM: You are a specialized {domain} extraction agent for a resume/CV parsing system.
Your task: extract {entity_type} from the provided text.
Rules:
1. Only extract information explicitly present in the text
2. If a field cannot be determined, set it to null or omit it
3. Assess your confidence for each extracted item
4. Do not fabricate or infer information not present
5. Return ONLY valid JSON matching the specified schema

USER: [Resume Text]
```

### 4.2 Example: Skills Extractor Prompt

```
You are a skills extraction agent for a resume/CV parsing system.
Your task: identify and categorize skills mentioned in the provided resume text.

Rules:
1. Extract ALL skills mentioned: programming languages, frameworks, databases,
   cloud platforms, tools, methodologies, and soft skills.
2. Categorize each skill: programming, cloud, database, framework, tool, soft, other.
3. Estimate years of experience if mentioned alongside the skill.
4. Do not infer skills from job titles alone (e.g., "Python Developer" does not
   guarantee 5 years of Python experience).
5. Assess confidence: high (explicitly stated with context), medium (mentioned
   without context), low (mentioned only in passing).
6. Return ONLY valid JSON.

Resume text:
{raw_text}
```

### 4.3 Example: Experience Extractor Prompt

```
You are a work experience extraction agent for a resume/CV parsing system.
Your task: extract structured work positions from the provided resume text.

Rules:
1. Extract each distinct position with company, title, and date range.
2. If employment type (full-time, contract, internship) is indicated, include it.
3. Extract the main responsibilities as bullet points (max 8 per position).
4. Extract tech stack mentions associated with each position.
5. For dates: use YYYY-MM format if available, YYYY if only year, null if unknown.
6. Set is_current=true only if the text explicitly states "present" or "current".
7. Assess confidence: high (clear structure with all key fields), medium (missing
   dates or description), low (vague or inferred).
8. Return ONLY valid JSON.

Resume text:
{raw_text}
```

## 5. Pydantic Output Schemas

### 5.1 Profile Extraction

```python
class ProfileExtractedField(BaseModel):
    field: str  # field name
    value: str
    confidence: Literal["high", "medium", "low"] = "medium"
    source_start: int | None = None  # char offset in source text
    source_end: int | None = None

class ProfileExtractionResult(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    headline: str | None = None
    links: list[str] = Field(default_factory=list)
    summary: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"
    field_details: list[ProfileExtractedField] = Field(default_factory=list)

    def to_candidates(self) -> list[dict]:
        """Convert to list of candidate dicts for ResumeIngestionCandidate."""
        # Returns one candidate per populated field + one for the summary
        ...
```

### 5.2 Experience Extraction

```python
class ExtractedPosition(BaseModel):
    company: str
    title: str
    start_date: str | None = None  # YYYY-MM or YYYY
    end_date: str | None = None
    is_current: bool = False
    employment_type: str | None = None
    description: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    location: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"

class ExperienceExtractionResult(BaseModel):
    positions: list[ExtractedPosition] = Field(default_factory=list)
    total_identified: int = 0

    def to_candidates(self) -> list[dict]:
        """One candidate per position."""
        ...
```

### 5.3 Common Patterns

All extraction results implement:

```python
class ExtractionResult(ABC):
    @abstractmethod
    def to_candidates(self) -> list[dict]:
        """Convert extraction result to list of candidate dicts."""
        ...
```

## 6. Entity Type Mapping

LLM extraction domains map to database entity types:

| Extraction Agent | Entity Type (DB) | Table |
|---|---|---|
| ProfileExtractor | `user_profile` | user_profiles |
| ExperienceExtractor | `position` | positions |
| EducationExtractor | `education` | educations |
| SkillsExtractor | `skill` | skills |
| ProjectsExtractor | `project` | projects |
| CertificationsExtractor | `certification` | certifications |
| AchievementsExtractor | `achievement` | achievements |

## 7. Error Handling & Fallback

### 7.1 LLM Unavailable

If `get_llm_client()` raises or returns a non-configured client:
- Fall back to rule-based `_parse_markdown_sections()` for Markdown/TXT
- Return HTTP 202 with status="processing" for PDF/DOCX (requires Celery worker)
- Log warning: "LLM extraction unavailable, using rule-based fallback"

### 7.2 Extraction Timeout

Set a 30-second timeout per agent. If an agent times out:
- Mark that domain as "extraction_failed"
- Log the timeout
- Continue with results from other agents
- User can manually add missing items in the review UI

### 7.3 Schema Validation Failure

If LLM returns output that doesn't match the Pydantic schema:
- Log the raw output and validation error
- Retry once with a simplified prompt (no schema, just JSON)
- If retry also fails, return empty results for that domain
- The review UI shows "Extraction failed for [domain] — please add manually"

### 7.4 Empty / Truncated Input

If raw_text is less than 50 characters:
- Return empty results for all domains
- Show message: "File content too short to extract meaningful data"

If raw_text is truncated to 8000 chars:
- Add a note to each candidate: "Source text was truncated to 8000 characters"
- Users can see the full text in the raw_markdown candidate

## 8. Testing Strategy

### 8.1 Unit Tests (Mock LLM)

```python
class TestProfileExtractor:
    async def test_extracts_name_email_location(self, mock_llm):
        ...

    async def test_returns_empty_when_no_profile_info(self, mock_llm):
        ...

    async def test_confidence_high_for_clear_fields(self, mock_llm):
        ...

class TestExperienceExtractor:
    async def test_extracts_multiple_positions(self, mock_llm):
        ...

    async def test_handles_missing_dates(self, mock_llm):
        ...

    async def test_detects_current_position(self, mock_llm):
        ...
```

### 8.2 Integration Tests

```python
class TestExtractionPipeline:
    async def test_full_resume_extraction_returns_all_domains(self, async_client):
        ...

    async def test_partial_extraction_respects_domain_filter(self, async_client):
        ...

    async def test_llm_unavailable_falls_back_to_rules(self, async_client):
        ...

    async def test_cached_results_avoid_llm_call(self, async_client):
        ...
```

### 8.3 Golden Tests

Maintain a set of fixture resumes with known expected extractions:

```
tests/fixtures/
  resume_software_engineer.md
  resume_new_grad.md
  resume_career_change.md
  resume_minimal.md
  expected/
    resume_software_engineer_profile.json
    resume_software_engineer_positions.json
    ...
```

These golden tests ensure prompt changes don't degrade extraction quality.

## 9. Performance Budget

| Metric | Target | Notes |
|---|---|---|
| Total extraction time | < 5 seconds | 7 parallel agents × ~3s each |
| Token usage (input) | < 8000 tokens | Raw text truncated at 8000 chars ≈ 2000 tokens |
| Token usage (output) | < 2000 tokens per agent | Structured JSON responses are compact |
| Cost per extraction (DeepSeek) | < $0.01 | ~10K input + ~2K output per agent × 7 |
| Cache hit rate target | > 80% | Files rarely change between uploads |

## 10. Future: User-Manageable Agents

The architecture is designed to support user customization in a future release:

```
┌─────────────────────────────────────────────────────┐
│              Agent Management UI (Future)            │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Prompt   │  │ Schema   │  │ Rules    │          │
│  │ Editor   │  │ Editor   │  │ Editor   │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                      │
│  User can:                                           │
│  - Edit extraction prompts per domain               │
│  - Add custom fields to extraction schemas           │
│  - Define post-processing rules                      │
│  - Set confidence thresholds                         │
│  - Create custom extraction agents for new domains   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

To enable this, the current implementation must:
1. Store prompts in the database, not hardcoded (use a `prompt_templates` table)
2. Make output schemas configurable (via JSON Schema stored in the database)
3. Support agent enable/disable per user
4. Log all extraction runs for debugging and improvement
5. Version all prompts and schemas

For MVP, prompts are hardcoded in `extraction_prompts.py` and schemas are Pydantic classes. The migration to database-stored prompts is a Phase 3+ enhancement.

## 11. Implementation Phases

### Phase E1: Foundation (4-6 hours)
- Create `app/agents/extraction/` package
- Create `app/schemas/extraction.py` with all Pydantic schemas
- Create `ExtractionOrchestrator` class
- Create base `ExtractionAgent` class
- Update `MockLLMClient._mock_structured()` with extraction schemas

### Phase E2: Extractors (6-8 hours)
- Implement all 7 extraction agents
- Write extraction prompt templates (versioned)
- Implement `to_candidates()` for all result types
- Unit tests for each extractor with mock LLM

### Phase E3: Integration (3-4 hours)
- Update `POST /api/ingestion/resume/upload` to use orchestrator
- Implement fallback to rule-based parser
- Add caching layer
- Integration tests

### Phase E4: Review UI Enhancements (2-3 hours)
- Update `app/ingestion/[id]/page.tsx` to show structured entity display
- Add confidence badges per candidate
- Show source text spans
- Add "Retry Extraction" button

### Phase E5: Testing & QA (2-3 hours)
- Golden tests with fixture resumes
- Performance benchmarks
- Error handling tests
- Manual QA with real resumes
