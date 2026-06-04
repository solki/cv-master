import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.resume_ingestion import ResumeIngestion, ResumeIngestionCandidate
from app.models.position import Position
from app.models.project import Project
from app.models.skill import Skill
from app.models.education import Education
from app.models.certification import Certification
from app.models.evidence import Evidence
from app.schemas.ingestion import (
    ResumeIngestionCreate,
    ResumeUploadResponse,
    CandidateResponse,
    CandidateUpdateRequest,
    IngestionStatusResponse,
    ImportResponse,
)
from app.services.crud import BaseCRUD
from app.ingestion.extractor import extract_text
from app.ingestion.parser import mock_parse_resume

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])
ingestion_crud = BaseCRUD(ResumeIngestion)
candidate_crud = BaseCRUD(ResumeIngestionCandidate)

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}

# Entity type mapping for import
ENTITY_MODELS = {
    "position": Position,
    "project": Project,
    "skill": Skill,
    "education": Education,
    "certification": Certification,
}


@router.post("/resume/upload", status_code=202)
async def upload_resume_pdf(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Upload a resume file, extract text, parse into candidate entities."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if f".{ext}" not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(ALLOWED_RESUME_EXTENSIONS))}",
        )

    # Read file content
    content = await file.read()

    # Step 1: Create ingestion record
    ingestion = await ingestion_crud.create(db, ResumeIngestionCreate(
        source_filename=file.filename,
        status="extracting",
    ))

    # Step 2: Extract text
    text, extract_error = await extract_text(file.filename, content)
    if extract_error:
        ingestion.error_message = extract_error
        ingestion.status = "failed"
        await db.flush()
        raise HTTPException(status_code=400, detail=extract_error)

    if not text:
        ingestion.error_message = "No text could be extracted from the file"
        ingestion.status = "failed"
        await db.flush()
        raise HTTPException(status_code=400, detail="No text could be extracted from the file")

    ingestion.status = "parsing"
    await db.flush()

    # Step 3: Parse into candidate entities (use mock parser for MVP)
    try:
        parsed = mock_parse_resume(text)
    except Exception as e:
        ingestion.error_message = f"Parse failed: {str(e)}"
        ingestion.status = "failed"
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

    # Step 4: Create candidate records
    entity_types = {
        "positions": "position",
        "projects": "project",
        "skills": "skill",
        "education": "education",
        "certifications": "certification",
    }

    candidate_count = 0
    for key, entity_type in entity_types.items():
        for item in parsed.get(key, []):
            confidence = "high" if entity_type == "skill" else "needs_review"
            candidate = ResumeIngestionCandidate(
                resume_ingestion_id=ingestion.id,
                entity_type=entity_type,
                extracted_data=item,
                confidence=confidence,
                status="pending",
            )
            db.add(candidate)
            candidate_count += 1

    # Add summary as a candidate too
    if parsed.get("summary"):
        candidate = ResumeIngestionCandidate(
            resume_ingestion_id=ingestion.id,
            entity_type="summary",
            extracted_data={"summary": parsed["summary"]},
            confidence="needs_review",
            status="pending",
        )
        db.add(candidate)
        candidate_count += 1

    ingestion.status = "review_ready"
    await db.flush()

    return ResumeUploadResponse(
        ingestion_id=ingestion.id,
        status="review_ready",
        candidate_count=candidate_count,
    )


@router.get("/resume/{ingestion_id}")
async def get_ingestion_status(ingestion_id: str, db: AsyncSession = Depends(get_db)):
    entity = await ingestion_crud.get(db, ingestion_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Ingestion not found")
    return IngestionStatusResponse.model_validate(entity)


@router.get("/resume/{ingestion_id}/candidates")
async def list_candidates(ingestion_id: str, db: AsyncSession = Depends(get_db)):
    query = select(ResumeIngestionCandidate).where(
        ResumeIngestionCandidate.resume_ingestion_id == ingestion_id
    ).order_by(ResumeIngestionCandidate.entity_type, ResumeIngestionCandidate.created_at)
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
    candidate.extracted_data = data.extracted_data
    await db.flush()
    return CandidateResponse.model_validate(candidate)


@router.post("/resume/{ingestion_id}/import")
async def import_candidates(ingestion_id: str, db: AsyncSession = Depends(get_db)):
    """Import accepted candidates into the career knowledge base."""
    ingestion = await ingestion_crud.get(db, ingestion_id)
    if ingestion is None:
        raise HTTPException(status_code=404, detail="Ingestion not found")

    query = select(ResumeIngestionCandidate).where(
        ResumeIngestionCandidate.resume_ingestion_id == ingestion_id,
        ResumeIngestionCandidate.status == "accepted",
    )
    result = await db.execute(query)
    accepted = result.scalars().all()

    created_ids: list[str] = []

    for candidate in accepted:
        entity_type = candidate.entity_type
        data = dict(candidate.extracted_data) if candidate.extracted_data else {}

        if entity_type in ENTITY_MODELS:
            model = ENTITY_MODELS[entity_type]
            # Map parsed fields to model fields
            entity = _create_entity(model, data)
            db.add(entity)
            await db.flush()
            created_ids.append(entity.id)

            # Create evidence record linking to the source ingestion
            evidence = Evidence(
                type="document",
                title=f"Imported {entity_type}: {_entity_label(entity_type, data)}",
                description=f"Extracted from uploaded resume: {ingestion.source_filename}",
                confidence=1.0,
                source_note_id=ingestion.id,
            )
            db.add(evidence)

    # Count rejected
    rejected_query = select(ResumeIngestionCandidate).where(
        ResumeIngestionCandidate.resume_ingestion_id == ingestion_id,
        ResumeIngestionCandidate.status == "rejected",
    )
    rejected_result = await db.execute(rejected_query)
    rejected = rejected_result.scalars().all()

    ingestion.status = "imported"
    await db.flush()

    return ImportResponse(
        ingestion_id=ingestion_id,
        imported_count=len(accepted),
        rejected_count=len(rejected),
        created_entity_ids=created_ids,
    )


def _create_entity(model, data: dict):
    """Create a model instance from parsed data dict."""
    field_maps = {
        Position: {
            "title": data.get("title", ""),
            "company": data.get("company", ""),
            "description": data.get("description", ""),
            "start_date": _parse_date(data.get("start_date")),
            "end_date": _parse_date(data.get("end_date")),
            "is_current": data.get("end_date") is None,
        },
        Project: {
            "title": data.get("title", ""),
            "organization": data.get("organization", ""),
            "role": data.get("role", ""),
            "summary": data.get("summary", ""),
            "skills": data.get("skills", ""),
            "domain": data.get("domain", ""),
        },
        Skill: {
            "name": data.get("name", ""),
            "category": data.get("category", "Other"),
            "proficiency": data.get("proficiency", 0.5),
        },
        Education: {
            "institution": data.get("institution", ""),
            "degree": data.get("degree", ""),
            "field": data.get("field", ""),
            "start_date": _parse_date(data.get("start_date")),
            "end_date": _parse_date(data.get("end_date")),
        },
        Certification: {
            "name": data.get("name", ""),
            "issuer": data.get("issuer", ""),
            "issued_at": _parse_date(data.get("issued_at")),
        },
    }

    kwargs = field_maps.get(model, {})
    return model(**kwargs)


def _parse_date(value):
    """Parse a date string to a Python date or return None."""
    if not value:
        return None
    from datetime import date
    for fmt in ("%Y-%m-%d", "%Y-%m", "%m/%Y", "%Y"):
        try:
            from datetime import datetime
            dt = datetime.strptime(str(value), fmt)
            return dt.date()
        except (ValueError, TypeError):
            continue
    return None


def _entity_label(entity_type: str, data: dict) -> str:
    """Get a human-readable label for an entity."""
    if entity_type == "position":
        return f"{data.get('title', '')} at {data.get('company', 'Unknown')}"
    if entity_type == "project":
        return data.get("title", "Untitled")
    if entity_type == "skill":
        return data.get("name", "Unknown")
    if entity_type == "education":
        return f"{data.get('degree', '')} - {data.get('institution', 'Unknown')}"
    if entity_type == "certification":
        return data.get("name", "Unknown")
    return "Unknown"
