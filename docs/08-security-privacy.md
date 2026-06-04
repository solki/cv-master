# Security And Privacy

## Privacy Posture

CV Master stores sensitive career and identity data. The MVP should be local-first and explicit about any network calls.

## Sensitive Data

Sensitive data includes:

- name and contact information
- employment history
- salary or compensation notes
- private project details
- internal company metrics
- recruiter communications
- generated resumes
- API keys

## LLM Provider Privacy

When cloud providers are configured, job descriptions and selected career context may be sent to external APIs. The UI and documentation should make this clear.

Local Ollama mode should avoid cloud LLM calls, but Tavily search remains external unless disabled or replaced.

## Secret Handling

- Store secrets in environment variables.
- Do not store API keys in generated logs.
- Do not return secret values from settings endpoints.
- Do not commit `.env`.
- Provide `.env.example` after implementation scaffolding.

## Resume Truthfulness

Security includes reputational safety. The system must avoid generating false claims.

Required controls:

- evidence references per claim
- confidence labels
- unsupported-claim warnings
- user review before final use
- generation audit records

## Data Access

MVP is single-user and local. Future phase 2 should add explicit profile scoping before supporting multiple profiles or shared access.

## Network Calls

Network integrations in MVP:

- configured LLM provider
- Tavily API
- optional source URL fetch for job descriptions

The backend should make network-capable services explicit and testable through adapters.

## File Safety

Vault and generated file paths should be configured. The API must prevent path traversal when reading or writing vault files.

## Logging

Logs should avoid raw resume content where possible. If raw prompts or completions are logged for debugging, that must be opt-in.

