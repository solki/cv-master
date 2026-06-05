"""Tests for the resume generation → version → export workflow."""

import pytest


class TestResumeVersionCreation:
    """Verify that generate creates a ResumeVersion row."""

    async def test_generate_creates_resume_version(self, async_client):
        """After generating a resume, a version record exists."""
        # Create a JD first (required for resume creation)
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "Test JD", "raw_text": "We need a Python developer"
        })
        assert jd_res.status_code == 201
        jd_id = jd_res.json()["id"]

        # Create a resume
        res = await async_client.post("/api/resumes", json={
            "title": "Test CV", "target_role": "Developer",
            "job_description_id": jd_id,
        })
        assert res.status_code == 201
        resume_id = res.json()["id"]

        # Generate — this should now create a version
        gen_res = await async_client.post(f"/api/resumes/{resume_id}/generate", json={
            "job_description_id": jd_id,
        })
        assert gen_res.status_code == 200
        data = gen_res.json()
        assert data["resume_id"] == resume_id
        assert data["status"] == "generated"

        # Verify versions exist
        ver_res = await async_client.get(f"/api/resumes/{resume_id}/versions")
        assert ver_res.status_code == 200
        versions = ver_res.json()
        assert len(versions) >= 1
        assert versions[0]["resume_id"] == resume_id
        assert versions[0]["version_number"] >= 1
        assert "content_json" in versions[0]

    async def test_multiple_generates_increment_version(self, async_client):
        """Each generate call creates a new version with incremented number."""
        # Setup: JD + resume
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "Version Test JD", "raw_text": "Python required"
        })
        jd_id = jd_res.json()["id"]
        res = await async_client.post("/api/resumes", json={
            "title": "Version Test CV", "target_role": "Dev",
            "job_description_id": jd_id,
        })
        resume_id = res.json()["id"]

        # Generate twice
        await async_client.post(f"/api/resumes/{resume_id}/generate", json={
            "job_description_id": jd_id,
        })
        await async_client.post(f"/api/resumes/{resume_id}/generate", json={
            "job_description_id": jd_id,
        })

        ver_res = await async_client.get(f"/api/resumes/{resume_id}/versions")
        versions = ver_res.json()
        assert len(versions) == 2
        # Versions sorted by version_number desc
        assert versions[0]["version_number"] == 2
        assert versions[1]["version_number"] == 1

    async def test_generate_nonexistent_resume_returns_404(self, async_client):
        res = await async_client.post("/api/resumes/nonexistent-id/generate", json={
            "job_description_id": "any-id",
        })
        assert res.status_code == 404


class TestExportWorkflow:
    """Verify export download with correct version ID."""

    async def test_export_download_with_valid_version(self, async_client):
        """Full workflow: JD → resume → generate → version → export download."""
        # Setup
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "Export JD", "raw_text": "Looking for a dev"
        })
        jd_id = jd_res.json()["id"]
        res = await async_client.post("/api/resumes", json={
            "title": "Export CV", "target_role": "Dev", "job_description_id": jd_id,
        })
        resume_id = res.json()["id"]
        gen_res = await async_client.post(f"/api/resumes/{resume_id}/generate", json={
            "job_description_id": jd_id,
        })
        assert gen_res.status_code == 200

        # Get the version ID
        ver_res = await async_client.get(f"/api/resumes/{resume_id}/versions")
        version_id = ver_res.json()[0]["id"]

        # Download markdown export using colon delimiter
        export_id = f"export_{version_id}:markdown"
        dl_res = await async_client.get(f"/api/exports/{export_id}/download")
        assert dl_res.status_code == 200
        assert "text/markdown" in dl_res.headers.get("content-type", "")

    async def test_export_download_html_format(self, async_client):
        """Export download works for HTML format."""
        # Setup
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "HTML Export JD", "raw_text": "Dev needed"
        })
        jd_id = jd_res.json()["id"]
        res = await async_client.post("/api/resumes", json={
            "title": "HTML CV", "target_role": "Dev", "job_description_id": jd_id,
        })
        resume_id = res.json()["id"]
        await async_client.post(f"/api/resumes/{resume_id}/generate", json={
            "job_description_id": jd_id,
        })
        ver_res = await async_client.get(f"/api/resumes/{resume_id}/versions")
        version_id = ver_res.json()[0]["id"]

        export_id = f"export_{version_id}:html"
        dl_res = await async_client.get(f"/api/exports/{export_id}/download")
        assert dl_res.status_code == 200
        assert "text/html" in dl_res.headers.get("content-type", "")

    async def test_export_nonexistent_version_returns_404(self, async_client):
        """Export of a non-existent version ID returns 404."""
        res = await async_client.get("/api/exports/export_fake-uuid:markdown/download")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    async def test_export_invalid_format_returns_400(self, async_client):
        """Export with bad format returns 400."""
        # Setup: create a real version
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "BadFmt JD", "raw_text": "Dev"
        })
        jd_id = jd_res.json()["id"]
        res = await async_client.post("/api/resumes", json={
            "title": "BadFmt CV", "target_role": "Dev", "job_description_id": jd_id,
        })
        resume_id = res.json()["id"]
        await async_client.post(f"/api/resumes/{resume_id}/generate", json={
            "job_description_id": jd_id,
        })
        ver_res = await async_client.get(f"/api/resumes/{resume_id}/versions")
        version_id = ver_res.json()[0]["id"]

        export_id = f"export_{version_id}:invalidfmt"
        dl_res = await async_client.get(f"/api/exports/{export_id}/download")
        assert dl_res.status_code == 400


class TestExportIDParsing:
    """Verify export ID format parsing is robust."""

    async def test_export_id_without_colon_returns_400(self, async_client):
        res = await async_client.get("/api/exports/export_someuuid_markdown/download")
        assert res.status_code == 400

    async def test_export_id_without_export_prefix_returns_400(self, async_client):
        res = await async_client.get("/api/exports/someuuid:markdown/download")
        assert res.status_code == 400


class TestJDAnalysis:
    """Tests for the JD analysis endpoint."""

    async def test_analyze_returns_structured_output(self, async_client):
        """Analysis returns job_title, seniority, skills."""
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "Test JD", "raw_text": "Senior Python Developer with FastAPI, Docker, AWS experience."
        })
        jd_id = jd_res.json()["id"]

        res = await async_client.post(f"/api/job-descriptions/{jd_id}/analyze")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert "analysis" in data
        analysis = data["analysis"]
        # Basic extraction should find Python as a skill
        assert "job_title" in analysis
        assert "required_skills" in analysis
        assert "ats_keywords" in analysis

    async def test_analyze_nonexistent_jd_returns_404(self, async_client):
        """Analysis of non-existent JD returns 404."""
        res = await async_client.post("/api/job-descriptions/fake-id/analyze")
        assert res.status_code == 404

    async def test_analysis_stored_on_jd(self, async_client):
        """After analysis, the JD record contains the analysis JSON."""
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "Store Test", "raw_text": "React developer with TypeScript skills."
        })
        jd_id = jd_res.json()["id"]

        await async_client.post(f"/api/job-descriptions/{jd_id}/analyze")

        # Fetch the JD and verify analysis is stored
        get_res = await async_client.get(f"/api/job-descriptions/{jd_id}")
        assert get_res.status_code == 200
        jd_data = get_res.json()
        assert jd_data["analysis"] != ""

    async def test_analyze_empty_jd_still_works(self, async_client):
        """Analysis of a JD with minimal text returns without error."""
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "Empty", "raw_text": "No real content here."
        })
        jd_id = jd_res.json()["id"]

        res = await async_client.post(f"/api/job-descriptions/{jd_id}/analyze")
        assert res.status_code == 200


class TestGenerateWorkflow:
    """Tests for the generate endpoint with real pipeline."""

    async def test_generate_handles_missing_jd(self, async_client):
        """Generate still works when JD is not found or empty."""
        # Create resume without JD
        res = await async_client.post("/api/resumes", json={
            "title": "No JD Resume", "target_role": "Developer",
        })
        resume_id = res.json()["id"]

        gen_res = await async_client.post(f"/api/resumes/{resume_id}/generate", json={
            "job_description_id": "",
        })
        assert gen_res.status_code == 200
        assert gen_res.json()["status"] == "generated"

    async def test_generate_stores_version_content(self, async_client):
        """Generated version has valid content_json."""
        jd_res = await async_client.post("/api/job-descriptions", json={
            "title": "Content JD", "raw_text": "Python dev"
        })
        jd_id = jd_res.json()["id"]
        res = await async_client.post("/api/resumes", json={
            "title": "Content CV", "target_role": "Dev", "job_description_id": jd_id,
        })
        resume_id = res.json()["id"]
        await async_client.post(f"/api/resumes/{resume_id}/generate", json={
            "job_description_id": jd_id,
        })

        ver_res = await async_client.get(f"/api/resumes/{resume_id}/versions")
        version = ver_res.json()[0]
        assert version["version_number"] >= 1
        assert version["content_json"] != ""
        import json
        content = json.loads(version["content_json"])
        assert "resume" in content
        assert "workflow_errors" in content
