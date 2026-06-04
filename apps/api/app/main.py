from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.routes.profile import router as profile_router
from app.api.routes.job_descriptions import router as jd_router
from app.api.routes.resumes import router as resumes_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.retrieval import router as retrieval_router
from app.api.routes.exports import router as exports_router
from app.api.routes.career_routers import (
    positions_router,
    projects_router,
    achievements_router,
    skills_router,
    educations_router,
    certifications_router,
    evidences_router,
)
from app.core.settings import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title="CV Master API",
        version="0.1.0",
        docs_url="/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health
    app.include_router(health_router)

    # Profile
    app.include_router(profile_router)

    # Career entity CRUD (7 routers)
    app.include_router(positions_router)
    app.include_router(projects_router)
    app.include_router(achievements_router)
    app.include_router(skills_router)
    app.include_router(educations_router)
    app.include_router(certifications_router)
    app.include_router(evidences_router)

    # Job Descriptions
    app.include_router(jd_router)

    # Resume Generation
    app.include_router(resumes_router)

    # Resume PDF Ingestion
    app.include_router(ingestion_router)

    # Knowledge Retrieval
    app.include_router(retrieval_router)

    # Exports
    app.include_router(exports_router)

    return app


app = create_app()
