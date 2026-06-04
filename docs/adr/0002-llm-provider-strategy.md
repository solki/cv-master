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

Required environment variables:

```env
LLM_PROVIDER=openai_compatible

OPENAI_COMPATIBLE_API_KEY=**********
OPENAI_COMPATIBLE_BASE_URL=https://api.deepseek.com
OPENAI_COMPATIBLE_MODEL=deepseek-v4-pro
OPENAI_COMPATIBLE_PROVIDER_NAME=deepseek

OPENAI_API_KEY=
OPENAI_MODEL=

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=

TAVILY_API_KEY=
```

Expected internal interface:

```text
LLMClient
  generate(messages, response_schema, options)
  stream(messages, response_schema, options)
  embed(texts, options)
```

If a provider does not support embeddings, implementation should use a separate embedding provider configuration rather than overloading the chat provider.

MVP search uses Tavily behind a `SearchProvider` interface:

```text
SearchProvider
  search(query, max_results, include_domains, exclude_domains)
```

Search is used for company and role context. It must not override verified user career facts.

## Rationale

This approach keeps the MVP flexible and supports future model changes. OpenAI-compatible APIs cover providers such as DeepSeek. Ollama supports local inference. Anthropic and OpenAI support high-quality cloud generation.

## Consequences

- Settings validation must be provider-specific.
- Structured output behavior may vary by provider and needs retry handling.
- Embedding support may require a separate embedding provider interface.
- Provider metadata must be stored on generation runs for reproducibility.
- The UI must make active provider and cloud/local privacy implications visible.

## References

- Pydantic Settings: https://pydantic.dev/
- Tavily API documentation: https://docs.tavily.com/
- Ollama: https://ollama.com/
