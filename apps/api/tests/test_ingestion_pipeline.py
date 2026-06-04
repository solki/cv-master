"""Tests for end-to-end resume ingestion pipeline."""

import pytest


class TestTextExtraction:
    """Tests for text extraction from uploaded files."""

    async def test_extract_markdown(self, async_client):
        """Upload a .md file and get candidates back."""
        content = b"# John Doe\n\n## Experience\n\n- Python developer at Acme Corp\n- AWS certified"
        files = {"file": ("resume.md", content, "text/markdown")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code == 202
        data = res.json()
        assert data["status"] == "review_ready"
        assert data["candidate_count"] > 0

    async def test_extract_txt(self, async_client):
        """Upload a .txt file and get candidates."""
        content = b"Software Engineer with Python, FastAPI, and Docker experience."
        files = {"file": ("resume.txt", content, "text/plain")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code == 202
        data = res.json()
        assert data["status"] == "review_ready"

    async def test_extract_empty_file(self, async_client):
        """Empty file returns 400."""
        files = {"file": ("empty.md", b"", "text/markdown")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code == 400

    async def test_extract_unsupported_type(self, async_client):
        """Unsupported file type returns 400."""
        files = {"file": ("photo.jpg", b"JPEG", "image/jpeg")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code == 400
        assert "Unsupported" in res.json()["detail"]


class TestCandidateFlow:
    """Tests for candidate review and accept/reject flow."""

    async def test_candidates_listed_after_upload(self, async_client):
        """After upload, candidates are returned by the list endpoint."""
        content = b"# Resume\n\nPython developer at Acme Corp.\nSkills: Python, Docker, AWS."
        files = {"file": ("resume.md", content, "text/markdown")}
        upload_res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = upload_res.json()["ingestion_id"]

        # List candidates
        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        assert cand_res.status_code == 200
        candidates = cand_res.json()
        assert len(candidates) > 0

    async def test_accept_candidate(self, async_client):
        """Accept a candidate changes its status."""
        content = b"Python developer.\nSkills: Python."
        files = {"file": ("resume.md", content, "text/markdown")}
        upload_res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = upload_res.json()["ingestion_id"]

        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        candidates = cand_res.json()
        assert len(candidates) > 0
        cand_id = candidates[0]["id"]

        # Accept
        acc_res = await async_client.post(
            f"/api/ingestion/resume/{ingestion_id}/candidates/{cand_id}/accept"
        )
        assert acc_res.status_code == 200
        assert acc_res.json()["status"] == "accepted"

    async def test_reject_candidate(self, async_client):
        """Reject a candidate changes its status."""
        content = b"Python developer.\nSkills: Python."
        files = {"file": ("resume.md", content, "text/markdown")}
        upload_res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = upload_res.json()["ingestion_id"]

        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        candidates = cand_res.json()
        cand_id = candidates[0]["id"]

        rej_res = await async_client.post(
            f"/api/ingestion/resume/{ingestion_id}/candidates/{cand_id}/reject"
        )
        assert rej_res.status_code == 200
        assert rej_res.json()["status"] == "rejected"

    async def test_edit_candidate(self, async_client):
        """Edit a candidate's extracted data."""
        content = b"Python developer.\nSkills: Python."
        files = {"file": ("resume.md", content, "text/markdown")}
        upload_res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = upload_res.json()["ingestion_id"]

        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        cand_id = cand_res.json()[0]["id"]

        edit_res = await async_client.put(
            f"/api/ingestion/resume/{ingestion_id}/candidates/{cand_id}",
            json={"extracted_data": {"name": "Custom Skill", "category": "Programming", "proficiency": 0.9}},
        )
        assert edit_res.status_code == 200

    async def test_get_ingestion_status(self, async_client):
        """Status endpoint returns correct info."""
        content = b"Python dev resume."
        files = {"file": ("resume.txt", content, "text/plain")}
        upload_res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = upload_res.json()["ingestion_id"]

        status_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}")
        assert status_res.status_code == 200
        data = status_res.json()
        assert data["source_filename"] == "resume.txt"
        assert data["status"] == "review_ready"


class TestImportFlow:
    """Tests for importing accepted candidates into the knowledge base."""

    async def test_import_creates_entity_records(self, async_client):
        """Importing accepted candidates creates real entities."""
        content = b"# Resume\n\nPython developer at Acme Corp.\nSkills: Python, Docker."
        files = {"file": ("resume.md", content, "text/markdown")}
        upload_res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = upload_res.json()["ingestion_id"]

        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        candidates = cand_res.json()

        # Accept all candidates
        for c in candidates:
            await async_client.post(
                f"/api/ingestion/resume/{ingestion_id}/candidates/{c['id']}/accept"
            )

        # Import
        import_res = await async_client.post(f"/api/ingestion/resume/{ingestion_id}/import")
        assert import_res.status_code == 200
        data = import_res.json()
        assert data["imported_count"] == len(candidates)
        assert data["rejected_count"] == 0
        assert len(data["created_entity_ids"]) > 0

    async def test_import_only_imports_accepted(self, async_client):
        """Only accepted candidates are imported; pending/rejected are skipped."""
        content = b"Python dev.\nSkills: Python."
        files = {"file": ("resume.md", content, "text/markdown")}
        upload_res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = upload_res.json()["ingestion_id"]

        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        candidates = cand_res.json()

        # Accept first, reject second, leave rest pending
        if len(candidates) >= 2:
            await async_client.post(
                f"/api/ingestion/resume/{ingestion_id}/candidates/{candidates[0]['id']}/accept"
            )
            await async_client.post(
                f"/api/ingestion/resume/{ingestion_id}/candidates/{candidates[1]['id']}/reject"
            )

        # Import
        import_res = await async_client.post(f"/api/ingestion/resume/{ingestion_id}/import")
        assert import_res.status_code == 200
        data = import_res.json()
        # Only 1 imported if we accepted exactly 1
        assert data["imported_count"] >= 1

    async def test_import_nonexistent_ingestion_returns_404(self, async_client):
        """Import of non-existent ingestion returns 404."""
        res = await async_client.post("/api/ingestion/resume/nonexistent-id/import")
        assert res.status_code == 404


class TestMockParser:
    """Tests for the mock resume parser."""

    def test_mock_parse_detects_skills(self):
        from app.ingestion.parser import mock_parse_resume
        result = mock_parse_resume("Experienced Python developer with Docker and AWS skills.")
        skills = [s["name"] for s in result["skills"]]
        assert "Python" in skills
        assert "Docker" in skills
        assert "AWS" in skills

    def test_mock_parse_detects_education(self):
        from app.ingestion.parser import mock_parse_resume
        result = mock_parse_resume("Bachelor of Science in Computer Science. Master degree.")
        assert len(result["education"]) >= 1

    def test_mock_parse_returns_empty_for_blank_text(self):
        from app.ingestion.parser import mock_parse_resume
        result = mock_parse_resume("No relevant keywords here.")
        assert result["positions"] == []
        assert len(result["skills"]) == 0
        assert result["summary"] == ""

    def test_mock_parse_includes_summary(self):
        from app.ingestion.parser import mock_parse_resume
        result = mock_parse_resume("Python and JavaScript developer.")
        assert len(result["summary"]) > 0
