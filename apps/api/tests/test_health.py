import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_health_llm(async_client: AsyncClient):
    response = await async_client.get("/health/llm")
    assert response.status_code == 200
    data = response.json()
    assert "llm" in data
    assert "search" in data
    assert data["llm"]["provider"] == "openai_compatible"


@pytest.mark.asyncio
async def test_api_docs_available(async_client: AsyncClient):
    response = await async_client.get("/docs")
    assert response.status_code == 200
