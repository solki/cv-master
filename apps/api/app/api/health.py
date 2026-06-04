from fastapi import APIRouter
from sqlalchemy import text

from app.core.settings import get_settings
from app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Returns API health and database connectivity status."""
    settings = get_settings()
    db_status = "ok"
    db_message = ""

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
    except Exception as e:
        db_status = "error"
        db_message = str(e)

    return {
        "status": "ok",
        "database": {"status": db_status, "message": db_message} if db_message else {"status": db_status},
        "environment": settings.APP_ENV,
    }


@router.get("/health/llm")
async def health_llm():
    """LLM provider configuration check. Does not expose secret values."""
    settings = get_settings()
    llm_status = settings.validate_provider_config()
    search_ok = settings.search_configured()

    return {
        "llm": llm_status,
        "search": {"configured": search_ok},
    }
