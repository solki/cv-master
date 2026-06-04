from typing import Any, AsyncIterator
from app.llm.base import LLMClient


class MockLLMClient(LLMClient):
    """Mock adapter for testing. Returns deterministic responses."""

    def __init__(self):
        self.call_history: list[dict] = []

    async def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> dict:
        self.call_history.append({"method": "generate", "messages": messages, "options": options})
        if response_schema:
            return self._mock_structured(response_schema)
        last_msg = messages[-1]["content"] if messages else ""
        return {"content": f"[Mock response to: {last_msg[:100]}]"}

    async def stream(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> AsyncIterator[str]:
        self.call_history.append({"method": "stream", "messages": messages})
        result = await self.generate(messages, response_schema, **options)
        content = result.get("content", "")
        for word in content.split():
            yield word + " "

    async def embed(self, texts: list[str], **options: Any) -> list[list[float]]:
        self.call_history.append({"method": "embed", "texts": texts})
        # Return mock embeddings (zeroth vector with small random-like values)
        import hashlib
        embeddings = []
        for text in texts:
            h = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
            vec = [(h >> i) & 0xFF / 255.0 for i in range(0, 1536, 10)]
            if len(vec) < 1536:
                vec = (vec * ((1536 // len(vec)) + 1))[:1536]
            embeddings.append(vec)
        return embeddings

    def _mock_structured(self, schema: dict) -> dict:
        """Return a minimal valid response for common schemas."""
        name = schema.get("name", "")
        if "jd_analysis" in name:
            return {
                "job_title": "Software Engineer",
                "seniority": "Mid-level",
                "required_skills": ["Python", "SQL"],
                "preferred_skills": ["Docker"],
                "responsibilities": ["Build and maintain services"],
                "domain_keywords": ["backend", "API"],
                "ats_keywords": ["Python", "REST", "agile"],
                "research_queries": [],
                "red_flags": [],
            }
        if "resume_strategy" in name:
            return {
                "target_positioning": "Experienced backend engineer",
                "recommended_template": "ats_compact",
                "section_order": ["summary", "experience", "skills"],
                "skills_emphasis": ["Python", "Backend"],
                "experience_emphasis": ["Recent backend roles"],
                "keyword_coverage_plan": "Emphasize Python and API keywords",
                "risks": [],
            }
        return {"result": "mock_structured_output"}
