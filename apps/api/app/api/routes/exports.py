from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.resume import ResumeVersion
from app.exports.renderer import ExportRenderer

router = APIRouter(prefix="/api/exports", tags=["exports"])
renderer = ExportRenderer()


@router.get("/{export_id}")
async def get_export_status(export_id: str):
    """Get export job status."""
    return {"export_id": export_id, "status": "ready"}


@router.get("/{export_id}/download")
async def download_export(export_id: str, db: AsyncSession = Depends(get_db)):
    """Download a generated export file.

    Export ID format: export_{version_id}:{format}
    The colon delimiter is safe because version_id is a UUID (no colons).
    """
    if not export_id.startswith("export_"):
        raise HTTPException(status_code=400, detail="Invalid export ID format")

    # Split on the LAST colon to extract format
    rest = export_id[len("export_"):]
    if ":" not in rest:
        raise HTTPException(status_code=400, detail="Invalid export ID: missing format delimiter")

    last_colon = rest.rfind(":")
    version_id = rest[:last_colon]
    fmt = rest[last_colon + 1:]

    if not version_id or not fmt:
        raise HTTPException(status_code=400, detail="Invalid export ID")

    from app.services.crud import BaseCRUD
    crud = BaseCRUD(ResumeVersion)
    version = await crud.get(db, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Resume version not found")

    import json
    content = json.loads(version.content_json) if version.content_json else {}

    if fmt == "markdown":
        md = renderer.render_markdown(content)
        return PlainTextResponse(content=md, media_type="text/markdown")
    elif fmt == "html":
        html = renderer.render_html(content)
        return Response(content=html, media_type="text/html")
    elif fmt == "pdf":
        pdf_bytes = renderer.render_pdf(content)
        return Response(content=pdf_bytes, media_type="application/pdf")
    elif fmt == "docx":
        docx_bytes = renderer.render_docx(content)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")
