from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.resume_ingestion import ResumeIngestion, ResumeIngestionCandidate
from app.schemas.ingestion import (
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


@router.post("/resume/upload", status_code=202)
async def upload_resume_pdf(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    ingestion = await ingestion_crud.create(db, ResumeIngestion(
        source_filename=file.filename,
        status="processing",
    ))
    # In the full implementation, this enqueues a Celery task for PDF extraction + LLM analysis
    return ResumeUploadResponse(ingestion_id=ingestion.id, status="processing")


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
