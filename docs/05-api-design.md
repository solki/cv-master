# API Design

## API Style

Use REST endpoints with JSON request and response bodies. Keep routes explicit and workflow-oriented.

## Health

```http
GET /health
GET /health/db
GET /health/llm
```

## Profiles

```http
GET /api/profile
PUT /api/profile
```

## Career Data

```http
GET /api/work-experiences
POST /api/work-experiences
GET /api/work-experiences/{id}
PUT /api/work-experiences/{id}
DELETE /api/work-experiences/{id}

GET /api/projects
POST /api/projects
GET /api/projects/{id}
PUT /api/projects/{id}
DELETE /api/projects/{id}

GET /api/skills
POST /api/skills
PUT /api/skills/{id}
DELETE /api/skills/{id}

GET /api/achievements
POST /api/achievements
PUT /api/achievements/{id}
DELETE /api/achievements/{id}

GET /api/education
POST /api/education
PUT /api/education/{id}
DELETE /api/education/{id}

GET /api/certifications
POST /api/certifications
PUT /api/certifications/{id}
DELETE /api/certifications/{id}
```

## Evidence

```http
GET /api/evidence
POST /api/evidence
GET /api/evidence/{id}
PUT /api/evidence/{id}
DELETE /api/evidence/{id}
POST /api/evidence/{id}/embed
```

## Job Descriptions

```http
POST /api/job-descriptions
GET /api/job-descriptions
GET /api/job-descriptions/{id}
POST /api/job-descriptions/{id}/analyze
```

## Resume Generation

```http
POST /api/resume-runs
GET /api/resume-runs
GET /api/resume-runs/{id}
GET /api/resume-runs/{id}/events
POST /api/resume-runs/{id}/cancel
```

Example create request:

```json
{
  "job_description_id": "uuid",
  "target_format": ["pdf", "markdown", "html", "docx"],
  "template_id": "ats-default",
  "target_length": "one_page",
  "tone": "professional",
  "constraints": {
    "avoid_unverified_metrics": true,
    "prefer_recent_experience": true
  }
}
```

## Resume Versions And Exports

```http
GET /api/resume-versions
GET /api/resume-versions/{id}
PUT /api/resume-versions/{id}
POST /api/resume-versions/{id}/export
GET /api/resume-versions/{id}/download/{format}
```

## Vault

```http
GET /api/vault/files
GET /api/vault/files/{path}
PUT /api/vault/files/{path}
POST /api/vault/sync
```

## Settings

```http
GET /api/settings/runtime
GET /api/settings/providers
POST /api/settings/providers/test
```

Provider settings should report configured status, not secret values.

## Error Model

Use a consistent error response:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

## Streaming And Status

Use server-sent events for generation progress in MVP. WebSockets can be added later if the personal assistant UI needs richer bidirectional interaction.

