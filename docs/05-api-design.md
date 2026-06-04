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
```

The analyze endpoint should enqueue a job and return a job ID.

### Retrieval

```http
POST /api/retrieval/search
POST /api/retrieval/profile-gap-analysis
```

Used by the frontend for previews and diagnostics.

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
