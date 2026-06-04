# Frontend Plan

## UX Direction

The frontend should be a professional productivity application, not a marketing site. The first screen should show the working resume generation workspace or dashboard.

Visual qualities:

- quiet, structured, dense enough for repeated work
- clear hierarchy
- strong editing ergonomics
- minimal decoration
- responsive layouts for desktop and tablet first, mobile second

## Primary Navigation

- Dashboard
- Career Profile
- Projects
- Evidence
- JD Analyzer
- Resume Generator
- Resume Library
- Vault
- Settings

## Key Screens

### Dashboard

Purpose:

- Show profile completeness
- Show recent resume runs
- Show missing evidence or weak areas
- Provide quick action to paste a JD
- Provide quick action to upload an existing resume (PDF) for bootstrapping the knowledge base

### Career Profile

Purpose:

- Manage work experience, education, certifications, skills, and achievements
- Show career timeline
- Link facts to evidence
- Import data via PDF resume upload: trigger upload, view extraction progress, review candidate snippets in a side-by-side or list interface, accept/reject/edit candidates, and confirm import into the knowledge base

### Projects

Purpose:

- Manage projects as reusable resume building blocks
- Capture role, technologies, domain, outcomes, metrics, and related experience

### Evidence

Purpose:

- Store raw supporting material
- Connect evidence to projects, achievements, and work experiences
- Show confidence status

### JD Analyzer

Purpose:

- Paste or load a job description (plain text, Markdown file upload, or website URL fetch)
- Show extracted requirements, keywords, and role analysis
- Highlight likely match/gap areas

### Resume Generator

Purpose:

- Select JD, template, length, tone, and output formats
- Show selected evidence before generation
- Display generation progress
- Show resume preview and critique findings
- Allow regeneration or targeted revision

### Resume Library

Purpose:

- Browse generated resume versions
- Compare versions
- Download outputs
- Inspect evidence traces

### Vault

Purpose:

- Browse Markdown career notes
- Edit local-readable career memory
- Trigger vault sync

### Settings

Purpose:

- Display active LLM provider
- Test provider connectivity
- Display Tavily configuration status
- Configure export defaults

## Component Strategy

Use shadcn/ui primitives for:

- tables
- forms
- dialogs
- tabs
- segmented controls
- tooltips
- command menus
- toasts
- side navigation

Use custom components for:

- career timeline
- evidence trace panel
- resume preview
- JD keyword coverage
- generation progress
- source confidence badges
- resume ingestion candidate review (side-by-side snippet list, accept/reject/edit controls, confidence indicator badges, batch accept/reject)

## State Management

- TanStack Query for server data
- Zustand for local UI state such as selected resume section and preview mode
- React Hook Form + Zod for career data forms

## Resume Preview

The preview should show:

- resume content
- ATS keyword coverage
- evidence trace for selected bullet
- critique warnings
- export buttons

## Accessibility

- All controls must be keyboard accessible.
- Forms must have clear labels and validation messages.
- Color should not be the only indicator of confidence or warning status.

