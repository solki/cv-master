"""Concrete CRUD router instances for each career entity."""
from app.models.position import Position
from app.models.project import Project
from app.models.achievement import Achievement
from app.models.skill import Skill
from app.models.education import Education
from app.models.certification import Certification
from app.models.evidence import Evidence
from app.schemas.positions import PositionCreate, PositionUpdate, PositionResponse
from app.schemas.projects import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.achievements import AchievementCreate, AchievementUpdate, AchievementResponse
from app.schemas.skills import SkillCreate, SkillUpdate, SkillResponse
from app.schemas.education import EducationCreate, EducationUpdate, EducationResponse
from app.schemas.certifications import CertificationCreate, CertificationUpdate, CertificationResponse
from app.schemas.evidences import EvidenceCreate, EvidenceUpdate, EvidenceResponse
from app.api.routes.career_entities import create_crud_router

positions_router = create_crud_router(
    prefix="/api/positions", tag="positions",
    model=Position,
    create_schema=PositionCreate, update_schema=PositionUpdate,
    response_schema=PositionResponse,
)

projects_router = create_crud_router(
    prefix="/api/projects", tag="projects",
    model=Project,
    create_schema=ProjectCreate, update_schema=ProjectUpdate,
    response_schema=ProjectResponse,
)

achievements_router = create_crud_router(
    prefix="/api/achievements", tag="achievements",
    model=Achievement,
    create_schema=AchievementCreate, update_schema=AchievementUpdate,
    response_schema=AchievementResponse,
)

skills_router = create_crud_router(
    prefix="/api/skills", tag="skills",
    model=Skill,
    create_schema=SkillCreate, update_schema=SkillUpdate,
    response_schema=SkillResponse,
)

educations_router = create_crud_router(
    prefix="/api/education", tag="education",
    model=Education,
    create_schema=EducationCreate, update_schema=EducationUpdate,
    response_schema=EducationResponse,
)

certifications_router = create_crud_router(
    prefix="/api/certifications", tag="certifications",
    model=Certification,
    create_schema=CertificationCreate, update_schema=CertificationUpdate,
    response_schema=CertificationResponse,
)

evidences_router = create_crud_router(
    prefix="/api/evidence", tag="evidence",
    model=Evidence,
    create_schema=EvidenceCreate, update_schema=EvidenceUpdate,
    response_schema=EvidenceResponse,
)
