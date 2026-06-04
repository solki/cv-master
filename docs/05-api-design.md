# API Design

## API Principles

- Use REST for MVP simplicity.
- Use JSON for request and response bodies.
- Keep long-running work asynchronous through job endpoints.
- Return stable IDs for all career facts and generated artifacts.
- Keep schemas typed and documented through FastAPI OpenAPI output.

## API Areas

### Health

```http
GET /health
```

Returns service health and dependency status.

### Profile

```http
GET /api/profile
PUT /api/profile
```

### Positions

```http
GET /api/positions
POST /api/positions
GET /api/positions/{position_id}
PUT /api/positions/{position_id}
DELETE /api/positions/{position_id}
```

### Projects

```http
GET /api/projects
POST /api/projects
GET /api/projects/{project_id}
PUT /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

### Achievements

```http
GET /api/achievements
POST /api/achievements
GET /api/achievements/{achievement_id}
PUT /api/achievements/{achievement_id}
DELETE /api/achievements/{achievement_id}
```

### Skills

```http
GET /api/skills
POST /api/skills
GET /api/skills/{skill_id}
PUT /api/skills/{skill_id}
DELETE /api/skills/{skill_id}
```

### Education And Certifications

```http
GET /api/education
POST /api/education
PUT /api/education/{education_id}
DELETE /api/education/{education_id}

GET /api/certifications
POST /api/certifications
PUT /api/certifications/{certification_id}
DELETE /api/certifications/{certification_id}
```

### Evidence

```http
GET /api/evidence
POST /api/evidence
GET /api/evidence/{evidence_id}
PUT /api/evidence/{evidence_id}
DELETE /api/evidence/{evidence_id}
```

### Job Descriptions

```http
GET /api/job-descriptions
POST /api/job-descriptions
GET /api/job-descriptions/{job_description_id}
POST /api/job-descriptions/{job_description_id}/analyze
POST /api/job-descriptions/fetch-url
POST /api/job-descriptions/upload-md
```

The `analyze` endpoint should enqueue a job and return a job ID.

The `fetch-url` endpoint accepts a URL, fetches its content, extracts plain text, and creates a `JobDescription` record with both `raw_text` and `source_url` populated.

The `upload-md` endpoint accepts a `.md` file upload, reads it as plain text, and creates a `JobDescription` record with `raw_text` populated.

### Retrieval

```http
POST /api/retrieval/search
POST /api/retrieval/profile-gap-analysis
```

Used by the frontend for previews and diagnostics.

### Resume Ingestion

```http
POST /api/ingestion/resume/upload
GET /api/ingestion/resume/{ingestion_id}
GET /api/ingestion/resume/{ingestion_id}/candidates
POST /api/ingestion/resume/{ingestion_id}/candidates/{candidate_id}/accept
POST /api/ingestion/resume/{ingestion_id}/candidates/{candidate_id}/reject
PUT /api/ingestion/resume/{ingestion_id}/candidates/{candidate_id}
POST /api/ingestion/resume/{ingestion_id}/import
```

Workflow:

1. `POST /api/ingestion/resume/upload` — accepts a PDF file. Extracts text from the PDF. Enqueues an LLM analysis job. Returns an `ingestion_id` and status `processing`.
2. `GET /api/ingestion/resume/{ingestion_id}` — returns the ingestion status (`processing`, `ready_for_review`, `imported`, `failed`) and metadata.
3. `GET /api/ingestion/resume/{ingestion_id}/candidates` — returns the list of candidate snippets with entity types, extracted data, and confidence labels (`high_confidence`, `needs_review`, `low_confidence`).
4. `POST .../candidates/{candidate_id}/accept` — marks a candidate as accepted.
5. `POST .../candidates/{candidate_id}/reject` — marks a candidate as rejected.
6. `PUT .../candidates/{candidate_id}` — updates a candidate with user edits before acceptance.
7. `POST .../import` — imports all accepted candidates into the knowledge base as structured records. Enqueues embedding generation and vault sync. Returns the created entity IDs.

### Resumes

```http
GET /api/resumes
POST /api/resumes
GET /api/resumes/{resume_id}
POST /api/resumes/{resume_id}/generate
GET /api/resumes/{resume_id}/versions
GET /api/resume-versions/{version_id}
PUT /api/resume-versions/{version_id}
POST /api/resume-versions/{version_id}/approve
```

### Exports

```http
POST /api/resume-versions/{version_id}/exports
GET /api/exports/{export_id}
GET /api/exports/{export_id}/download
```

Supported export formats:

- `markdown`
- `html`
- `pdf`
- `docx`

### Jobs

```http
GET /api/jobs/{job_id}
```

Returns:

- `queued`
- `running`
- `succeeded`
- `failed`
- `cancelled`

## Example Resume Generate Request

```json
{
  "job_description_id": "jd_01H...",
  "template_id": "ats_compact",
  "target_format": "pdf",
  "include_research": true,
  "max_pages": 2
}
```

## Example Resume Generate Response

```json
{
  "job_id": "job_01H...",
  "resume_id": "resume_01H...",
  "status": "queued"
}
```

## Error Model

Use a consistent error structure:

```json
{
  "error": {
    "code": "unsupported_claim",
    "message": "The generated bullet contains a metric that is not supported by evidence.",
    "details": {
      "evidence_required": true
    }
  }
}
```

## Future API Extensions

- WebSocket or Server-Sent Events for live agent progress.
- Authentication for private remote deployment.
- Assistant conversation endpoints.
- Job application tracker endpoints.
