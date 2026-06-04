from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.resume_ingestion import ResumeIngestion, ResumeIngestionCandidate
from app.schemas.ingestion import (
    ResumeIngestionCreate,
    ResumeUploadResponse,
    CandidateResponse,
    CandidateUpdateRequest,
    IngestionStatusResponse,
    ImportResponse,
)
from app.services.crud import BaseCRUD

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])
ingestion_crud = BaseCRUD(ResumeIngestion)
candidate_crud = BaseCRUD(ResumeIngestionCandidate)

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}


@router.post("/resume/upload", status_code=202)
async def upload_resume_pdf(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if f".{ext}" not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(ALLOWED_RESUME_EXTENSIONS))}",
        )

    # Read file content
    try:
        content = await file.read()
        raw_text = content.decode("utf-8", errors="replace") if content else ""
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="File is empty")

    # Create ingestion record
    ingestion = await ingestion_crud.create(db, ResumeIngestionCreate(
        source_filename=file.filename,
        status="processing",
    ))

    # Parse markdown into candidate sections
    candidates_created = _parse_markdown_sections(db, ingestion.id, raw_text)
    await db.flush()

    ingestion.status = "parsed"
    await db.flush()

    return ResumeUploadResponse(
        ingestion_id=ingestion.id,
        status="parsed",
    )


def _parse_markdown_sections(db, ingestion_id: str, raw_text: str) -> int:
    """Parse markdown content into ResumeIngestionCandidate records.

    Splits on ## headers, maps header text to entity types, creates candidates.
    Returns the number of candidates created.
    """
    import re

    ENTITY_TYPE_MAP: dict[str, str] = {
        "profile": "user_profile",
        "contact": "user_profile",
        "experience": "position",
        "work": "position",
        "positions": "position",
        "position": "position",
        "education": "education",
        "skills": "skill",
        "skill": "skill",
        "projects": "project",
        "project": "project",
        "certifications": "certification",
        "certification": "certification",
        "achievements": "achievement",
        "achievement": "achievement",
        "evidence": "evidence",
        "summary": "user_profile",
    }

    # Split by ## headers (level 2 only — main sections)
    sections = re.split(r"\n(?=## )", raw_text)
    candidates_created = 0

    for section in sections:
        # Extract the header line
        header_match = re.match(r"^(?:#|##)\s+(.+?)(?:\n|$)", section)
        if not header_match:
            # Content before the first ## header — treat as profile summary
            header_text = "summary"
            section_content = section.strip()
        else:
            header_text = header_match.group(1).strip().lower()
            # Remove the header from content
            section_content = section[header_match.end():].strip()

        if not section_content:
            continue

        # Map to entity type
        entity_type = None
        for key, etype in ENTITY_TYPE_MAP.items():
            if key in header_text:
                entity_type = etype
                break

        if entity_type is None:
            entity_type = "other"

        # Build extracted data
        extracted_data = {
            "header": header_text,
            "content": section_content,
            "source_section": section_content[:500],
        }

        candidate = ResumeIngestionCandidate(
            resume_ingestion_id=ingestion_id,
            entity_type=entity_type,
            extracted_data=extracted_data,
            confidence="needs_review",
            status="pending",
        )
        db.add(candidate)
        candidates_created += 1

    # Also add the full raw text as a "raw_markdown" candidate for reference
    db.add(ResumeIngestionCandidate(
        resume_ingestion_id=ingestion_id,
        entity_type="raw_markdown",
        extracted_data={"content": raw_text, "filename": ""},
        confidence="needs_review",
        status="pending",
    ))

    return candidates_created + 1


@router.get("/resume/{ingestion_id}")
async def get_ingestion_status(ingestion_id: str, db: AsyncSession = Depends(get_db)):
    entity = await ingestion_crud.get(db, ingestion_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Ingestion not found")
    return IngestionStatusResponse.model_validate(entity)


@router.get("/resume/{ingestion_id}/candidates")
async def list_candidates(ingestion_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    query = select(ResumeIngestionCandidate).where(
        ResumeIngestionCandidate.resume_ingestion_id == ingestion_id
    )
    result = await db.execute(query)
    candidates = result.scalars().all()
    return [CandidateResponse.model_validate(c) for c in candidates]


@router.post("/resume/{ingestion_id}/candidates/{candidate_id}/accept")
async def accept_candidate(ingestion_id: str, candidate_id: str, db: AsyncSession = Depends(get_db)):
    candidate = await candidate_crud.get(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.status = "accepted"
    await db.flush()
    return {"status": "accepted"}


@router.post("/resume/{ingestion_id}/candidates/{candidate_id}/reject")
async def reject_candidate(ingestion_id: str, candidate_id: str, db: AsyncSession = Depends(get_db)):
    candidate = await candidate_crud.get(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.status = "rejected"
    await db.flush()
    return {"status": "rejected"}


@router.put("/resume/{ingestion_id}/candidates/{candidate_id}")
async def edit_candidate(
    ingestion_id: str, candidate_id: str,
    data: CandidateUpdateRequest, db: AsyncSession = Depends(get_db),
):
    candidate = await candidate_crud.get(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.user_edits = data.extracted_data
    await db.flush()
    return CandidateResponse.model_validate(candidate)


@router.post("/resume/{ingestion_id}/import")
async def import_candidates(ingestion_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    ingestion = await ingestion_crud.get(db, ingestion_id)
    if ingestion is None:
        raise HTTPException(status_code=404, detail="Ingestion not found")
    query = select(ResumeIngestionCandidate).where(
        ResumeIngestionCandidate.resume_ingestion_id == ingestion_id,
        ResumeIngestionCandidate.status == "accepted",
    )
    result = await db.execute(query)
    accepted = result.scalars().all()
    ingestion.status = "imported"
    return ImportResponse(
        ingestion_id=ingestion_id,
        imported_count=len(accepted),
        rejected_count=0,
        created_entity_ids=[c.id for c in accepted],
    )
