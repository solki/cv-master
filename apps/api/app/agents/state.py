from typing import TypedDict, Optional, Any


class ResumeWorkflowState(TypedDict, total=False):
    """Typed state for the resume generation LangGraph workflow."""

    # Inputs
    job_description_id: str
    raw_jd_text: str

    # Stage outputs
    jd_analysis: Optional[dict]
    research_context: Optional[list[dict]]
    retrieved_items: Optional[list[dict]]
    resume_strategy: Optional[dict]
    draft_resume: Optional[dict]
    ats_review: Optional[dict]
    grounding_review: Optional[dict]

    # User interaction
    user_edits: Optional[dict]
    approved: bool
    export_requests: Optional[list[str]]

    # Control
    errors: list[str]
    needs_revision: bool
    current_stage: str
    revision_count: int
