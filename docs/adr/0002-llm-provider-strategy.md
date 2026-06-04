# ADR 0002: LLM Provider Strategy

## Status

Accepted for MVP planning.

## Context

The system must support both cloud LLM quality and local model privacy. The user wants provider selection through `LLM_PROVIDER`, including OpenAI-compatible APIs and Ollama.

## Decision

Implement provider adapters for:

- `openai_compatible`
- `openai`
- `anthropic`
- `ollama`

The rest of the application should call internal interfaces rather than provider SDKs directly.

## Rationale

This approach keeps the MVP flexible and supports future model changes. OpenAI-compatible APIs cover providers such as DeepSeek. Ollama supports local inference. Anthropic and OpenAI support high-quality cloud generation.

## Consequences

- Settings validation must be provider-specific.
- Structured output behavior may vary by provider and needs retry handling.
- Embedding support may require a separate embedding provider interface.
- Provider metadata must be stored on generation runs for reproducibility.

