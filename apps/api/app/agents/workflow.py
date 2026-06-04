"""LangGraph resume generation workflow with 8 stages."""

import json
from typing import Optional
from langgraph.graph import StateGraph, END
from app.agents.state import ResumeWorkflowState
from app.agents.prompts.templates import (
    JD_ANALYSIS_PROMPT,
    RESUME_STRATEGY_PROMPT,
    RESUME_WRITER_PROMPT,
    ATS_REVIEW_PROMPT,
    GROUNDING_REVIEW_PROMPT,
)
from app.llm import get_llm_client


def _format_state(state: ResumeWorkflowState) -> str:
    return json.dumps({k: v for k, v in state.items() if k not in ("errors",)}, default=str, indent=2)


async def analyze_jd_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """Stage 1: Analyze the job description."""
    state["current_stage"] = "analyze_jd"
    llm = get_llm_client()
    prompt = JD_ANALYSIS_PROMPT.format(jd_text=state.get("raw_jd_text", ""))

    try:
        result = await llm.generate(
            messages=[{"role": "user", "content": prompt}],
            response_schema={"name": "jd_analysis", "strict": True},
        )
        state["jd_analysis"] = result
    except Exception as e:
        state["errors"].append(f"JD analysis failed: {str(e)}")
        state["jd_analysis"] = {"error": str(e)}

    return state


async def research_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """Stage 2: Optional company/role research."""
    state["current_stage"] = "research"
    # In MVP this is optional. Use Tavily if configured.
    try:
        from app.search.tavily_adapter import TavilySearchProvider
        search = TavilySearchProvider()
        jd = state.get("jd_analysis", {})
        query = f"{jd.get('job_title', '')} company culture"
        results = await search.search(query, max_results=3)
        state["research_context"] = results
    except Exception:
        state["research_context"] = []
    return state


async def retrieve_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """Stage 3: Retrieve relevant career evidence."""
    state["current_stage"] = "retrieve"
    # In the full implementation, this uses RetrievalService.hybrid_search
    state["retrieved_items"] = []
    return state


async def strategy_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """Stage 4: Plan resume strategy."""
    state["current_stage"] = "strategy"
    llm = get_llm_client()
    prompt = RESUME_STRATEGY_PROMPT.format(
        jd_analysis=json.dumps(state.get("jd_analysis", {})),
        retrieved_items=json.dumps(state.get("retrieved_items", [])),
    )
    try:
        result = await llm.generate(
            messages=[{"role": "user", "content": prompt}],
            response_schema={"name": "resume_strategy", "strict": True},
        )
        state["resume_strategy"] = result
    except Exception as e:
        state["errors"].append(f"Strategy failed: {str(e)}")
        state["resume_strategy"] = {"error": str(e)}
    return state


async def draft_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """Stage 5: Draft resume sections."""
    state["current_stage"] = "draft"
    llm = get_llm_client()
    prompt = RESUME_WRITER_PROMPT.format(
        strategy=json.dumps(state.get("resume_strategy", {})),
        retrieved_items=json.dumps(state.get("retrieved_items", [])),
    )
    try:
        result = await llm.generate(
            messages=[{"role": "user", "content": prompt}],
            response_schema={"name": "resume_draft", "strict": True},
        )
        state["draft_resume"] = result
    except Exception as e:
        state["errors"].append(f"Draft failed: {str(e)}")
        state["draft_resume"] = {"error": str(e)}
    return state


async def ats_review_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """Stage 6: ATS and recruiter review."""
    state["current_stage"] = "ats_review"
    llm = get_llm_client()
    jd = state.get("jd_analysis", {})
    prompt = ATS_REVIEW_PROMPT.format(
        resume_json=json.dumps(state.get("draft_resume", {})),
        ats_keywords=", ".join(jd.get("ats_keywords", [])),
        target_seniority=jd.get("seniority", "mid"),
    )
    try:
        result = await llm.generate(
            messages=[{"role": "user", "content": prompt}],
            response_schema={"name": "ats_review", "strict": True},
        )
        state["ats_review"] = result
    except Exception as e:
        state["errors"].append(f"ATS review failed: {str(e)}")
        state["ats_review"] = {"error": str(e)}
    return state


async def grounding_review_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """Stage 7: Truthfulness and evidence grounding review."""
    state["current_stage"] = "grounding_review"
    llm = get_llm_client()
    prompt = GROUNDING_REVIEW_PROMPT.format(
        resume_json=json.dumps(state.get("draft_resume", {})),
        evidence_records=json.dumps(state.get("retrieved_items", [])),
    )
    try:
        result = await llm.generate(
            messages=[{"role": "user", "content": prompt}],
            response_schema={"name": "grounding_review", "strict": True},
        )
        state["grounding_review"] = result
        unsupported = result.get("unsupported_count", 0)
        needs_fix = result.get("confirmation_required", [])
        state["needs_revision"] = unsupported > 0 or len(needs_fix) > 0
    except Exception as e:
        state["errors"].append(f"Grounding review failed: {str(e)}")
        state["grounding_review"] = {"error": str(e)}
        state["needs_revision"] = True
    return state


def should_revise(state: ResumeWorkflowState) -> str:
    if state.get("needs_revision", False):
        return "draft"
    return "user_review"


def is_approved(state: ResumeWorkflowState) -> str:
    if state.get("approved", False):
        return "export"
    return END


def build_resume_workflow() -> StateGraph:
    workflow = StateGraph(ResumeWorkflowState)

    workflow.add_node("analyze_jd", analyze_jd_node)
    workflow.add_node("research", research_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("strategy", strategy_node)
    workflow.add_node("draft", draft_node)
    workflow.add_node("ats_review", ats_review_node)
    workflow.add_node("grounding_review", grounding_review_node)

    workflow.set_entry_point("analyze_jd")
    workflow.add_edge("analyze_jd", "research")
    workflow.add_edge("research", "retrieve")
    workflow.add_edge("retrieve", "strategy")
    workflow.add_edge("strategy", "draft")
    workflow.add_edge("draft", "ats_review")
    workflow.add_edge("ats_review", "grounding_review")
    workflow.add_conditional_edges("grounding_review", should_revise, {
        "draft": "draft",
        "user_review": END,
    })

    return workflow.compile()


async def run_resume_generation(jd_text: str, job_description_id: str = "") -> ResumeWorkflowState:
    """Run the full resume generation workflow."""
    workflow = build_resume_workflow()
    initial_state: ResumeWorkflowState = {
        "job_description_id": job_description_id,
        "raw_jd_text": jd_text,
        "jd_analysis": None,
        "research_context": None,
        "retrieved_items": None,
        "resume_strategy": None,
        "draft_resume": None,
        "ats_review": None,
        "grounding_review": None,
        "user_edits": None,
        "approved": False,
        "export_requests": None,
        "errors": [],
        "needs_revision": False,
        "current_stage": "init",
    }
    result = await workflow.ainvoke(initial_state)
    return result
