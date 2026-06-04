import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_profile_crud(async_client: AsyncClient):
    # Get or create profile
    resp = await async_client.get("/api/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "full_name" in data

    # Update profile
    resp = await async_client.put("/api/profile", json={"full_name": "Test User"})
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Test User"


@pytest.mark.asyncio
async def test_positions_crud(async_client: AsyncClient):
    # Create
    resp = await async_client.post("/api/positions", json={
        "company": "TestCorp", "title": "Engineer"
    })
    assert resp.status_code == 201
    pos_id = resp.json()["id"]

    # List
    resp = await async_client.get("/api/positions")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # Get
    resp = await async_client.get(f"/api/positions/{pos_id}")
    assert resp.status_code == 200
    assert resp.json()["company"] == "TestCorp"

    # Update
    resp = await async_client.put(f"/api/positions/{pos_id}", json={"title": "Senior Engineer"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Senior Engineer"

    # Delete
    resp = await async_client.delete(f"/api/positions/{pos_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_projects_crud(async_client: AsyncClient):
    resp = await async_client.post("/api/projects", json={
        "title": "Test Project", "organization": "TestOrg"
    })
    assert resp.status_code == 201
    assert resp.json()["title"] == "Test Project"

    proj_id = resp.json()["id"]
    resp = await async_client.delete(f"/api/projects/{proj_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_skills_crud(async_client: AsyncClient):
    resp = await async_client.post("/api/skills", json={
        "name": "Python", "category": "Programming", "proficiency": 4.0
    })
    assert resp.status_code == 201
    assert resp.json()["name"] == "Python"

    skill_id = resp.json()["id"]
    resp = await async_client.delete(f"/api/skills/{skill_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_education_crud(async_client: AsyncClient):
    resp = await async_client.post("/api/education", json={
        "institution": "Test University", "degree": "BSc", "field": "CS"
    })
    assert resp.status_code == 201
    edu_id = resp.json()["id"]
    resp = await async_client.delete(f"/api/education/{edu_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_evidence_crud(async_client: AsyncClient):
    resp = await async_client.post("/api/evidence", json={
        "type": "document", "title": "Performance Review"
    })
    assert resp.status_code == 201
    ev_id = resp.json()["id"]
    resp = await async_client.delete(f"/api/evidence/{ev_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_jd_crud(async_client: AsyncClient):
    resp = await async_client.post("/api/job-descriptions", json={
        "title": "Software Engineer", "company": "HireCorp",
        "raw_text": "We are looking for a Python developer..."
    })
    assert resp.status_code == 201
    jd_id = resp.json()["id"]

    resp = await async_client.get(f"/api/job-descriptions/{jd_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_resume_crud(async_client: AsyncClient):
    resp = await async_client.post("/api/resumes", json={
        "title": "My Resume", "target_role": "Backend Developer"
    })
    assert resp.status_code == 201
    resume_id = resp.json()["id"]

    resp = await async_client.get(f"/api/resumes/{resume_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_not_found(async_client: AsyncClient):
    resp = await async_client.get("/api/positions/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_validation_error(async_client: AsyncClient):
    # profile update with wrong type
    resp = await async_client.put("/api/profile", json={"full_name": 123})
    assert resp.status_code == 422
