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
    """Download a generated export file."""
    parts = export_id.split("_")
    if len(parts) < 3:
        raise HTTPException(status_code=400, detail="Invalid export ID")

    fmt = parts[-1]
    # export_id format: export_{version_id}_{format}
    version_id = export_id[len("export_"):-len(f"_{fmt}")]

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
