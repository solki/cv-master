# Testing And Quality Plan

## Testing Goals

- Verify career data CRUD flows.
- Verify retrieval quality enough for MVP use.
- Verify resume generation is grounded in evidence.
- Verify exports are readable and professional.
- Verify provider configuration works across cloud and local modes.

## Backend Tests

Use pytest.

Test categories:

- settings validation
- LLM provider adapter selection
- search provider adapter behavior
- database model constraints
- API route validation
- retrieval ranking
- agent node structured outputs
- export rendering
- evidence trace enforcement

## Frontend Tests

Use the project-standard Next.js testing stack once scaffolded.

Test categories:

- form validation
- navigation
- resume generation job creation
- progress/status rendering
- preview rendering
- settings provider status display

## Integration Tests

Run with Docker Compose:

- API health check
- DB health check
- Alembic migration
- sample profile creation
- sample JD analysis
- sample resume generation with mocked LLM
- export generation

## Golden Tests

Maintain a small set of sample profiles and job descriptions. Expected outputs should not be exact full text matches, but tests should verify:

- required sections exist
- unsupported claims are absent
- evidence references exist
- important keywords are covered
- length constraints are respected

## Manual QA Checklist

- Can the user enter a work experience?
- Can the user add a project and link it to a job?
- Can the user add evidence?
- Can the user paste a JD?
- Does the analysis identify required skills?
- Does generation select relevant projects?
- Does the resume avoid unsupported claims?
- Can the user export PDF, Markdown, HTML, and DOCX?
- Are generated files visually clean?

## Quality Gates

Before claiming a feature is complete:

- run backend tests
- run frontend tests or linting
- run relevant Docker Compose smoke tests
- inspect generated resume output manually for at least one sample

