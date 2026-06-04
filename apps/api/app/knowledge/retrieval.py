from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.embedding import Embedding
from app.knowledge.embedding import EmbeddingService


class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def hybrid_search(
        self,
        db: AsyncSession,
        query: str,
        entity_types: list[str] | None = None,
        top_k: int = 10,
    ) -> list[dict]:
        """Hybrid retrieval combining keyword and semantic search.

        Returns ranked list of {entity_type, entity_id, text, score} dicts.
        If pgvector is unavailable, falls back to keyword-only search.
        """
        results: list[dict] = []

        # Keyword search via PostgreSQL full-text search
        results = await self._keyword_search(db, query, entity_types, top_k)

        # Try vector search if pgvector is available
        try:
            vector_results = await self._vector_search(db, query, entity_types, top_k)
            results = self._merge_results(results, vector_results, top_k)
        except Exception:
            pass  # Vector search not available (e.g. SQLite in tests)

        return results[:top_k]

    async def _keyword_search(
        self,
        db: AsyncSession,
        query: str,
        entity_types: list[str] | None,
        top_k: int,
    ) -> list[dict]:
        conditions = []
        if entity_types:
            placeholders = ",".join(f":t{i}" for i in range(len(entity_types)))
            conditions.append(f"entity_type IN ({placeholders})")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        # Simple ILIKE-based keyword search (simulated FTS without tsvector dependency)
        sql = f"""
            SELECT entity_type, entity_id, text
            FROM embeddings
            WHERE {where_clause} AND text ILIKE :query_pattern
            ORDER BY char_length(text) ASC
            LIMIT :limit
        """
        params = {"query_pattern": f"%{query}%", "limit": top_k}
        if entity_types:
            for i, et in enumerate(entity_types):
                params[f"t{i}"] = et

        try:
            result = await db.execute(text(sql), params)
            rows = result.fetchall()
            return [
                {
                    "entity_type": r[0],
                    "entity_id": r[1],
                    "text": r[2],
                    "score": 0.5,  # base keyword score
                }
                for r in rows
            ]
        except Exception:
            return []

    async def _vector_search(
        self,
        db: AsyncSession,
        query: str,
        entity_types: list[str] | None,
        top_k: int,
    ) -> list[dict]:
        query_embedding = await self.embedding_service.embed_single(query)
        embedding_str = ",".join(str(v) for v in query_embedding)

        conditions = []
        if entity_types:
            placeholders = ",".join(f":t{i}" for i in range(len(entity_types)))
            conditions.append(f"entity_type IN ({placeholders})")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
            SELECT entity_type, entity_id, text,
                   1 - (embedding <=> ARRAY[{embedding_str}]::vector) AS similarity
            FROM embeddings
            WHERE {where_clause}
            ORDER BY similarity DESC
            LIMIT :limit
        """
        params = {"limit": top_k}
        if entity_types:
            for i, et in enumerate(entity_types):
                params[f"t{i}"] = et

        result = await db.execute(text(sql), params)
        rows = result.fetchall()
        return [
            {
                "entity_type": r[0],
                "entity_id": r[1],
                "text": r[2],
                "score": float(r[3]),
            }
            for r in rows
        ]

    def _merge_results(
        self,
        keyword_results: list[dict],
        vector_results: list[dict],
        top_k: int,
    ) -> list[dict]:
        merged: dict[str, dict] = {}

        for r in keyword_results:
            key = f"{r['entity_type']}:{r['entity_id']}"
            merged[key] = {"keyword_score": r["score"], "vector_score": 0.0, **r}

        for r in vector_results:
            key = f"{r['entity_type']}:{r['entity_id']}"
            if key in merged:
                merged[key]["vector_score"] = r["score"]
                merged[key]["score"] = 0.4 * merged[key]["keyword_score"] + 0.6 * r["score"]
            else:
                merged[key] = {"keyword_score": 0.0, "vector_score": r["score"], **r}

        return sorted(merged.values(), key=lambda r: r["score"], reverse=True)[:top_k]
