"""Tests for file upload endpoints and CORS behavior."""

import os
import pytest


class TestCORS:
    """Verify CORS headers and preflight handling."""

    async def test_cors_preflight_allows_localhost_3000(self, async_client):
        """OPTIONS preflight from allowed origin returns CORS headers."""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
        res = await async_client.options("/api/ingestion/resume/upload", headers=headers)
        assert res.status_code == 200
        assert "access-control-allow-origin" in res.headers
        assert res.headers["access-control-allow-origin"] == "http://localhost:3000"

    async def test_cors_preflight_allows_127_0_0_1(self, async_client):
        """OPTIONS preflight from 127.0.0.1 also allowed."""
        headers = {
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
        }
        res = await async_client.options("/api/job-descriptions/upload-md", headers=headers)
        assert res.status_code == 200
        assert "access-control-allow-origin" in res.headers

    async def test_cors_headers_present_on_post(self, async_client):
        """POST response includes CORS headers for allowed origin."""
        # Upload a valid PDF file
        pdf_content = b"%PDF-1.4 test pdf content"
        files = {"file": ("test_resume.pdf", pdf_content, "application/pdf")}
        headers = {"Origin": "http://localhost:3000"}
        res = await async_client.post(
            "/api/ingestion/resume/upload", files=files, headers=headers
        )
        assert "access-control-allow-origin" in res.headers

    async def test_cors_headers_on_error_response(self, async_client):
        """Error responses still include CORS headers."""
        files = {"file": ("bad.xyz", b"content", "application/octet-stream")}
        headers = {"Origin": "http://localhost:3000"}
        res = await async_client.post(
            "/api/ingestion/resume/upload", files=files, headers=headers
        )
        assert res.status_code == 400
        assert "access-control-allow-origin" in res.headers


class TestResumeMarkdownParsing:
    """Tests for markdown resume upload and candidate creation."""

    async def test_upload_markdown_creates_candidates(self, async_client):
        """Uploading a markdown resume creates candidate records from sections."""
        md_content = b"""# John Doe

## Summary
Experienced software engineer with 10 years in the industry.

## Experience
Senior Developer at TechCorp (2020-2024)
- Led team of 5 engineers
- Built microservices architecture

## Education
MIT, BSc Computer Science, 2015

## Skills
Python, FastAPI, PostgreSQL, Docker, Kubernetes

## Projects
Data Pipeline - Real-time ETL processing 1M events/day

## Certifications
AWS Solutions Architect, 2023
"""
        files = {"file": ("resume.md", md_content, "text/markdown")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code == 202
        data = res.json()
        assert data["status"] == "parsed"
        ingestion_id = data["ingestion_id"]

        # Verify candidates were created
        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        assert cand_res.status_code == 200
        candidates = cand_res.json()
        assert len(candidates) >= 1, f"Expected at least 1 candidate, got {len(candidates)}"

        # Verify entity types are correctly mapped
        types = [c["entity_type"] for c in candidates]
        assert "position" in types, f"Expected 'position' in entity types, got {types}"
        assert "skill" in types, f"Expected 'skill' in entity types, got {types}"
        assert "education" in types, f"Expected 'education' in entity types, got {types}"

    async def test_upload_markdown_candidates_have_correct_status(self, async_client):
        """Newly created candidates have 'pending' status."""
        md_content = b"## Skills\nPython, Docker"
        files = {"file": ("skills.md", md_content, "text/markdown")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = res.json()["ingestion_id"]

        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        for c in cand_res.json():
            assert c["status"] == "pending"
            assert c["confidence"] == "needs_review"

    async def test_accept_candidate_works(self, async_client):
        """Accepting a candidate changes its status."""
        md_content = b"## Skills\nPython"
        files = {"file": ("skills.md", md_content, "text/markdown")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = res.json()["ingestion_id"]

        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        candidate_id = cand_res.json()[0]["id"]

        acc_res = await async_client.post(
            f"/api/ingestion/resume/{ingestion_id}/candidates/{candidate_id}/accept"
        )
        assert acc_res.status_code == 200
        assert acc_res.json()["status"] == "accepted"

    async def test_reject_candidate_works(self, async_client):
        """Rejecting a candidate changes its status."""
        md_content = b"## Skills\nPython"
        files = {"file": ("skills.md", md_content, "text/markdown")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = res.json()["ingestion_id"]

        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        candidate_id = cand_res.json()[0]["id"]

        rej_res = await async_client.post(
            f"/api/ingestion/resume/{ingestion_id}/candidates/{candidate_id}/reject"
        )
        assert rej_res.status_code == 200
        assert rej_res.json()["status"] == "rejected"

    async def test_import_only_imports_accepted(self, async_client):
        """Import only counts accepted candidates."""
        md_content = b"## Skills\nPython\n\n## Experience\nSenior Dev at Acme"
        files = {"file": ("resume.md", md_content, "text/markdown")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = res.json()["ingestion_id"]

        cand_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}/candidates")
        candidates = cand_res.json()

        # Accept only the first candidate
        await async_client.post(
            f"/api/ingestion/resume/{ingestion_id}/candidates/{candidates[0]['id']}/accept"
        )

        # Import
        imp_res = await async_client.post(f"/api/ingestion/resume/{ingestion_id}/import")
        assert imp_res.status_code == 200
        data = imp_res.json()
        assert data["imported_count"] == 1


class TestResumeUpload:
    """Tests for resume PDF ingestion endpoint."""

    async def test_upload_pdf_success(self, async_client):
        """Uploading a valid .pdf file creates an ingestion record and parses it."""
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\nxref\n0 1\ntrailer\n<<>>\nstartxref\n9\n%%EOF"
        files = {"file": ("my_resume.pdf", pdf_content, "application/pdf")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code == 202
        data = res.json()
        assert "ingestion_id" in data
        assert data["status"] in ("processing", "parsed")

    async def test_upload_docx_accepted(self, async_client):
        """Uploading a .docx file is now accepted."""
        files = {"file": ("resume.docx", b"DOCX content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code == 202

    async def test_upload_md_accepted(self, async_client):
        """Uploading a .md file is accepted."""
        files = {"file": ("resume.md", b"# My Resume\n\nContent", "text/markdown")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code == 202

    async def test_upload_unsupported_type(self, async_client):
        """Uploading an unsupported file type returns 400 with clear message."""
        files = {"file": ("photo.jpg", b"JPEG data", "image/jpeg")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code == 400
        detail = res.json()["detail"]
        assert "Unsupported file type" in detail
        assert ".jpg" in detail

    async def test_upload_no_file(self, async_client):
        """Missing file returns 422 validation error."""
        res = await async_client.post("/api/ingestion/resume/upload")
        assert res.status_code == 422

    async def test_upload_empty_filename(self, async_client):
        """File with empty filename returns 400."""
        files = {"file": ("", b"content", "application/pdf")}
        res = await async_client.post("/api/ingestion/resume/upload", files=files)
        assert res.status_code in (400, 422)

    async def test_can_get_ingestion_status_after_upload(self, async_client):
        """After uploading, the ingestion status endpoint returns the record."""
        files = {"file": ("test.pdf", b"%PDF-1.4", "application/pdf")}
        upload_res = await async_client.post("/api/ingestion/resume/upload", files=files)
        ingestion_id = upload_res.json()["ingestion_id"]

        status_res = await async_client.get(f"/api/ingestion/resume/{ingestion_id}")
        assert status_res.status_code == 200
        assert status_res.json()["source_filename"] == "test.pdf"
        assert status_res.json()["status"] in ("processing", "parsed")


class TestJDUpload:
    """Tests for JD markdown upload endpoint."""

    async def test_upload_md_success(self, async_client):
        """Uploading a .md file creates a JD record."""
        files = {"file": ("job.md", b"# Senior Engineer\n\nWe are looking for...", "text/markdown")}
        res = await async_client.post("/api/job-descriptions/upload-md", files=files)
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "job.md"
        assert data["source_type"] == "md_upload"
        assert data["source_filename"] == "job.md"
        assert "Senior Engineer" in data["raw_text"]

    async def test_upload_txt_accepted(self, async_client):
        """Uploading a .txt file is accepted."""
        files = {"file": ("job.txt", b"Looking for a Python dev", "text/plain")}
        res = await async_client.post("/api/job-descriptions/upload-md", files=files)
        assert res.status_code == 201

    async def test_upload_unsupported_extension(self, async_client):
        """Uploading a .pdf returns 400 for JD endpoint."""
        files = {"file": ("job.pdf", b"%PDF-1.4", "application/pdf")}
        res = await async_client.post("/api/job-descriptions/upload-md", files=files)
        assert res.status_code == 400
        detail = res.json()["detail"]
        assert "Unsupported" in detail

    async def test_upload_empty_file(self, async_client):
        """Uploading an empty file returns 400."""
        files = {"file": ("empty.md", b"", "text/markdown")}
        res = await async_client.post("/api/job-descriptions/upload-md", files=files)
        assert res.status_code == 400
        assert "empty" in res.json()["detail"].lower()

    async def test_upload_no_file(self, async_client):
        """Missing file returns 422."""
        res = await async_client.post("/api/job-descriptions/upload-md")
        assert res.status_code == 422

    async def test_uploaded_jd_appears_in_list(self, async_client):
        """After upload, the JD appears in the GET list."""
        files = {"file": ("listing.md", b"# Job Listing\n\nDetails here", "text/markdown")}
        await async_client.post("/api/job-descriptions/upload-md", files=files)

        list_res = await async_client.get("/api/job-descriptions")
        assert list_res.status_code == 200
        titles = [item["title"] for item in list_res.json()["items"]]
        assert "listing.md" in titles


class TestJDFetchURL:
    """Tests for JD fetch-url endpoint error classification."""

    async def test_fetch_url_http_404_returns_400(self, async_client):
        """A 404 from the target URL returns 400 or 502 with clear message."""
        res = await async_client.post("/api/job-descriptions/fetch-url", json={
            "url": "https://example.com/nonexistent-page-12345",
        })
        # 400 for client error from target; 502 if network fails
        assert res.status_code in (400, 502)
        detail = res.json()["detail"].lower()
        assert any(word in detail for word in ["404", "not found", "unreachable", "could not", "failed"])

    async def test_fetch_url_invalid_host_returns_502(self, async_client):
        """An unreachable host returns 400 or 502 with network error message."""
        res = await async_client.post("/api/job-descriptions/fetch-url", json={
            "url": "https://invalid.host.that.does.not.exist.example",
        })
        assert res.status_code in (400, 502)
        # Should not return raw stack trace
        assert "traceback" not in res.json()["detail"].lower()
