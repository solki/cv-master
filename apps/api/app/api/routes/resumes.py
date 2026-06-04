from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.resume import Resume, ResumeVersion, ResumeBulletEvidence
from app.schemas.resumes import (
    ResumeCreate,
    ResumeResponse,
    ResumeGenerateRequest,
    ResumeGenerateResponse,
    ResumeVersionResponse,
    ResumeVersionUpdate,
    ExportRequest,
    ExportResponse,
    BulletEvidenceResponse,
)
from app.schemas.common import paginated_response
from app.services.crud import BaseCRUD

router = APIRouter(prefix="/api", tags=["resumes"])
resume_crud = BaseCRUD(Resume)
version_crud = BaseCRUD(ResumeVersion)
bullet_crud = BaseCRUD(ResumeBulletEvidence)


@router.get("/resumes")
async def list_resumes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    items, total = await resume_crud.list(db, offset=offset, limit=limit)
    return paginated_response(
        [ResumeResponse.model_validate(item) for item in items],
        total, offset, limit,
    )


@router.post("/resumes", status_code=201)
async def create_resume(data: ResumeCreate, db: AsyncSession = Depends(get_db)):
    entity = await resume_crud.create(db, data)
    return ResumeResponse.model_validate(entity)


@router.get("/resumes/{resume_id}")
async def get_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    entity = await resume_crud.get(db, resume_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return ResumeResponse.model_validate(entity)


@router.post("/resumes/{resume_id}/generate")
async def generate_resume(
    resume_id: str, data: ResumeGenerateRequest, db: AsyncSession = Depends(get_db)
):
    resume = await resume_crud.get(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return ResumeGenerateResponse(
        job_id=f"job_{resume_id}", resume_id=resume_id, status="queued"
    )


@router.get("/resumes/{resume_id}/versions")
async def list_versions(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    query = (
        select(ResumeVersion)
        .where(ResumeVersion.resume_id == resume_id)
        .order_by(ResumeVersion.version_number.desc())
    )
    result = await db.execute(query)
    versions = result.scalars().all()
    return [ResumeVersionResponse.model_validate(v) for v in versions]


@router.get("/resume-versions/{version_id}")
async def get_version(version_id: str, db: AsyncSession = Depends(get_db)):
    entity = await version_crud.get(db, version_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return ResumeVersionResponse.model_validate(entity)


@router.put("/resume-versions/{version_id}")
async def update_version(
    version_id: str, data: ResumeVersionUpdate, db: AsyncSession = Depends(get_db)
):
    entity = await version_crud.update(db, version_id, data)
    if entity is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return ResumeVersionResponse.model_validate(entity)


@router.post("/resume-versions/{version_id}/approve")
async def approve_version(version_id: str, db: AsyncSession = Depends(get_db)):
    version = await version_crud.get(db, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")
    resume = await resume_crud.get(db, version.resume_id)
    if resume:
        resume.status = "approved"
    return {"status": "approved", "version_id": version_id}


@router.post("/resume-versions/{version_id}/exports")
async def request_export(
    version_id: str, data: ExportRequest, db: AsyncSession = Depends(get_db)
):
    version = await version_crud.get(db, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return ExportResponse(export_id=f"export_{version_id}_{data.format}", status="queued")
