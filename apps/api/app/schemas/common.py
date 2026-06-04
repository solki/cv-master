from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class PaginationParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


class JobResponse(BaseModel):
    job_id: str
    status: str


def paginated_response(items: list, total: int, offset: int, limit: int) -> dict:
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
    }
