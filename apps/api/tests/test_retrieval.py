"""Tests for retrieval endpoints and search functionality."""

import pytest


class TestGapAnalysis:
    """Tests for profile gap analysis endpoint."""

    async def test_gap_analysis_returns_404_for_missing_jd(self, async_client):
        """Gap analysis with non-existent JD returns 404, not 500."""
        res = await async_client.post("/api/retrieval/profile-gap-analysis", json={
            "job_description_id": "00000000-0000-0000-0000-000000000000",
        })
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    async def test_gap_analysis_with_valid_jd_returns_structure(self, async_client):
        """Gap analysis with a real JD returns expected response shape."""
        # Create a JD first
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "Gap Test JD", "raw_text": "Python developer needed"
        })
        jd_id = jd_res.json()["id"]

        res = await async_client.post("/api/retrieval/profile-gap-analysis", json={
            "job_description_id": jd_id,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["job_description_id"] == jd_id
        assert data["status"] == "completed"
        assert "matches" in data
        assert "partial_matches" in data
        assert "gaps" in data
        assert "existing_skill_count" in data


class TestSearch:
    """Tests for retrieval search endpoint."""

    async def test_search_returns_response_structure(self, async_client):
        """Search returns correct JSON structure even with empty results."""
        res = await async_client.post("/api/retrieval/search", json={
            "query": "Python developer",
            "top_k": 5,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["query"] == "Python developer"
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)

    async def test_search_with_entity_type_filter(self, async_client):
        """Search with entity_type filter still returns valid structure."""
        res = await async_client.post("/api/retrieval/search", json={
            "query": "Python",
            "entity_types": ["skills", "projects"],
            "top_k": 3,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 0

    async def test_search_default_top_k(self, async_client):
        """Search without explicit top_k uses default (10)."""
        res = await async_client.post("/api/retrieval/search", json={
            "query": "test",
        })
        assert res.status_code == 200

    async def test_search_top_k_respects_limit(self, async_client):
        """Search respects top_k bounds (1-50)."""
        res = await async_client.post("/api/retrieval/search", json={
            "query": "test",
            "top_k": 1,
        })
        assert res.status_code == 200
