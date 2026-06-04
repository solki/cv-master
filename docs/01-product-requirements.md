# Product Requirements

## Product Vision

CV Master helps a user turn their complete career history into targeted, truthful, ATS-friendly resumes for specific jobs. It should feel like a focused personal career assistant with memory, not a generic chatbot.

## Primary User

The MVP user is one individual managing their own career materials locally or in a private deployment.

## Main User Problem

High-quality resume targeting is repetitive and error-prone. A user often has many projects, achievements, technologies, and career events, but a resume should only include the most relevant subset for a specific job description. The system must help select, rewrite, and format that subset while preserving truthfulness.

## Success Criteria

- The generated resume is credible to recruiters and hiring managers.
- The resume includes relevant ATS keywords without keyword stuffing.
- The resume highlights the strongest matching experiences and projects.
- The user can trace generated claims back to their career records.
- Exported files are clean, professional, and compatible with common screening tools.

## MVP Scope

### Career Knowledge Management

- Work experiences
- Education
- Certifications
- Projects
- Achievements
- Skills
- Career events and timeline notes
- Evidence items such as links, documents, metrics, and raw notes
- Markdown vault export/sync for local-readable career memory
- PDF resume upload and parsing: the user can upload an existing resume in PDF format. The system extracts structured information (positions, projects, skills, education, etc.) and presents them as candidate snippets. The user reviews and selects which snippets to import into the career knowledge base.

### Resume Generation

- Paste a job description, upload a Markdown JD file, or provide a JD website URL for the agent to fetch and parse
- Analyze role, seniority, responsibilities, hard requirements, nice-to-have requirements, keywords, and risks
- Retrieve matching career facts
- Generate resume strategy
- Generate ATS-friendly resume draft
- Run critique for truthfulness, ATS fit, readability, and formatting
- Export to PDF, Markdown, HTML, and DOCX

### Settings

- LLM provider selection
- Provider-specific API keys and model names through environment variables
- Tavily API key
- Export template preference

## Out Of Scope For MVP

- Multi-user account system
- Billing
- Job board integrations
- Automatic application submission
- Email/calendar automation
- Voice interface
- Enterprise permissions

## Phase 2 Direction

Phase 2 should become a specialized personal career assistant. Candidate capabilities:

- career memory chat
- interview preparation from resume and JD
- application tracker
- recruiter communication drafting
- weekly career progress capture
- richer local knowledge graph
- optional desktop/app integrations

## Product Quality Bar

The MVP should prioritize one reliable resume generation workflow over many shallow features. The generated resume must be useful enough that the user would edit it lightly, not rewrite it from scratch.

