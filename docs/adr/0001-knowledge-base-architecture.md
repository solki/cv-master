# ADR 0001: Career Knowledge Base Architecture

## Status

Accepted for MVP planning.

## Context

CV Master needs a knowledge system that supports:

- user ownership and local readability
- structured career data
- semantic retrieval
- keyword retrieval for ATS terms
- truthful resume generation with evidence references
- future evolution into a personal career assistant

Benchmarks considered:

- Obsidian-style local Markdown vaults
- Mem0-style agent memory
- QBrain/ZBrain-style enterprise knowledge bases

The user referenced "Qbrian"; this document treats that as the QBrain/ZBrain-style category of AI knowledge-base products unless a more specific project is later identified.

## Comparison

| Approach | Strengths | Weaknesses | Fit For CV Master |
| --- | --- | --- | --- |
| Obsidian-style local vault | Local-first, transparent Markdown files, easy manual editing, durable personal knowledge | Markdown alone is hard to query reliably; relationships, dates, and evidence confidence need structure | Excellent as the human-readable layer |
| QBrain/ZBrain-style enterprise knowledge base | Strong document ingestion, organizational search, enterprise workflows | Too broad for a single-user MVP; may add permissions, connectors, and workflow complexity too early | Useful inspiration for future document ingestion, not the MVP core |
| Mem0-style memory layer | Designed for long-term AI memory, useful for personalized assistants and chat continuity | Memory is not the same as an auditable fact system; risk of opaque or stale claims | Good post-MVP assistant memory layer |
| Structured Postgres + pgvector | Queryable, auditable, versionable, supports relational integrity and vector search | Requires more upfront schema design | Best canonical data layer |

## Decision

Use a hybrid architecture:

- Postgres is the source of truth for structured career facts.
- Markdown vault stores local-readable career notes and generated artifacts.
- pgvector stores semantic embeddings.
- Postgres full-text search supports exact keyword and ATS terminology matching.
- Resume generation must reference source entities and evidence.

Recommended local vault shape:

```text
knowledge-vault/
  profile.md
  work/
  projects/
  education/
  certifications/
  skills/
  stories/
  evidence/
```

Markdown notes should include stable frontmatter IDs that link back to database records.

Example:

```yaml
---
id: project_01H...
type: project
title: "Customer Segmentation Pipeline"
source_record: projects.project_01H...
confidence: user_verified
---
```

## Rationale

Obsidian-style Markdown vaults are excellent for ownership, portability, and user editing, but weak as the only source of structured facts. Mem0-style memory is promising for phase 2 assistant behavior, but less direct for strict resume auditability. Enterprise knowledge-base patterns are useful for retrieval, but too heavy as the product model for a personal MVP.

The hybrid approach keeps MVP complexity manageable while preserving phase 2 extensibility.

## Consequences

- The app must maintain sync rules between Postgres and Markdown.
- The agent must retrieve from structured and text sources.
- The user can inspect data in both the app and local files.
- Future assistant features can reuse the same memory foundation.

## References

- Obsidian data storage: https://help.obsidian.md/Files+and+folders/How+Obsidian+stores+data
- Mem0 documentation: https://docs.mem0.ai/
- pgvector: https://github.com/pgvector/pgvector
