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

## Decision

Use a hybrid architecture:

- Postgres is the source of truth for structured career facts.
- Markdown vault stores local-readable career notes and generated artifacts.
- pgvector stores semantic embeddings.
- Postgres full-text search supports exact keyword and ATS terminology matching.
- Resume generation must reference source entities and evidence.

## Rationale

Obsidian-style Markdown vaults are excellent for ownership, portability, and user editing, but weak as the only source of structured facts. Mem0-style memory is promising for phase 2 assistant behavior, but less direct for strict resume auditability. Enterprise knowledge-base patterns are useful for retrieval, but too heavy as the product model for a personal MVP.

The hybrid approach keeps MVP complexity manageable while preserving phase 2 extensibility.

## Consequences

- The app must maintain sync rules between Postgres and Markdown.
- The agent must retrieve from structured and text sources.
- The user can inspect data in both the app and local files.
- Future assistant features can reuse the same memory foundation.

