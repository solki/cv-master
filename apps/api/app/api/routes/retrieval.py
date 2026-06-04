from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from app.db.session import get_db
from app.knowledge.retrieval import RetrievalService

router = APIRouter(prefix="/api/retrieval", tags=["retrieval"])


class SearchRequest(BaseModel):
    query: str
    entity_types: list[str] | None = None
    top_k: int = Field(default=10, ge=1, le=50)


class GapAnalysisRequest(BaseModel):
    job_description_id: str


@router.post("/search")
async def search(request: SearchRequest, db: AsyncSession = Depends(get_db)):
    service = RetrievalService()
    results = await service.hybrid_search(
        db,
        query=request.query,
        entity_types=request.entity_types,
        top_k=request.top_k,
    )
    return {"query": request.query, "results": results, "total": len(results)}


@router.post("/profile-gap-analysis")
async def profile_gap_analysis(request: GapAnalysisRequest, db: AsyncSession = Depends(get_db)):
    """
    Compare a target JD against the user profile and report gaps.
    In the full implementation, this uses the LLM to analyze gaps.
    """
    from app.services.crud import BaseCRUD
    from app.models.job_description import JobDescription
    from app.models.skill import Skill

    jd_crud = BaseCRUD(JobDescription)
    jd = await jd_crud.get(db, request.job_description_id)
    if jd is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job description not found")

    skill_crud = BaseCRUD(Skill)
    existing_skills, _ = await skill_crud.list(db, limit=500)

    return {
        "job_description_id": request.job_description_id,
        "existing_skill_count": len(existing_skills),
        "status": "completed",
        "matches": [],
        "partial_matches": [],
        "gaps": [],
    }
