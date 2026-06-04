from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.job_description import JobDescription
from app.schemas.job_descriptions import JDCreate, JDFetchURLRequest, JDResponse
from app.schemas.common import paginated_response, JobResponse
from app.services.crud import BaseCRUD

router = APIRouter(prefix="/api/job-descriptions", tags=["job_descriptions"])
crud = BaseCRUD(JobDescription)


@router.get("")
async def list_jds(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    items, total = await crud.list(db, offset=offset, limit=limit)
    return paginated_response(
        [JDResponse.model_validate(item) for item in items],
        total, offset, limit,
    )


@router.post("", status_code=201)
async def create_jd(data: JDCreate, db: AsyncSession = Depends(get_db)):
    entity = await crud.create(db, data)
    return JDResponse.model_validate(entity)


@router.get("/{jd_id}")
async def get_jd(jd_id: str, db: AsyncSession = Depends(get_db)):
    entity = await crud.get(db, jd_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Job description not found")
    return JDResponse.model_validate(entity)


@router.post("/fetch-url", status_code=201)
async def fetch_jd_url(data: JDFetchURLRequest, db: AsyncSession = Depends(get_db)):
    """Fetch a JD from a URL, extract text, and create a JobDescription."""
    import httpx
    from bs4 import BeautifulSoup
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(data.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            raw_text = soup.get_text(separator="\n", strip=True)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Target URL returned HTTP {e.response.status_code}. The page may not exist or may be inaccessible.",
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=502, detail="Request timed out while fetching the URL. The server may be unreachable.")
    except httpx.ConnectError:
        raise HTTPException(status_code=502, detail="Could not connect to the URL. Check that the address is correct and the server is reachable.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {str(e)}")

    entity = await crud.create(db, JDCreate(
        raw_text=raw_text[:50000],
        source_url=data.url,
        source_type="url",
    ))
    return JDResponse.model_validate(entity)


@router.post("/upload-md", status_code=201)
async def upload_jd_md(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Upload a Markdown or text JD file and create a JobDescription."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if ext not in ("md", "txt"):
        raise HTTPException(status_code=400, detail=f"Unsupported file type '.{ext}'. Allowed: .md, .txt")
    try:
        content = await file.read()
        raw_text = content.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="File is empty")

    entity = await crud.create(db, JDCreate(
        title=file.filename,
        raw_text=raw_text[:50000],
        source_type="md_upload",
        source_filename=file.filename,
    ))
    await db.refresh(entity)
    return JDResponse.model_validate(entity)


@router.post("/{jd_id}/analyze")
async def analyze_jd(jd_id: str, db: AsyncSession = Depends(get_db)):
    """Enqueue JD analysis job."""
    jd = await crud.get(db, jd_id)
    if jd is None:
        raise HTTPException(status_code=404, detail="Job description not found")
    # In milestone 6 this will enqueue a real Celery task
    return JobResponse(job_id=f"job_{jd_id}", status="queued")
