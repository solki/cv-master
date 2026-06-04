"""LLM-based resume parser.

Parses extracted resume text into structured career entities using the
existing LLM provider adapter layer. Falls back to mock parsing for tests.
"""

import json
from app.llm.base import LLMClient

RESUME_PARSING_PROMPT = """You are a resume parser. Extract structured career information from the resume text below.

Return a JSON object with these keys:
- positions: list of {company, title, start_date (YYYY-MM), end_date (YYYY-MM or null if current), description (1-2 sentences)}
- projects: list of {title, organization, role, summary (1-2 sentences), skills (comma-separated), domain}
- skills: list of {name, category (Programming|Framework|Tool|Cloud|Soft Skill|Language|Other), proficiency (0.0-1.0)}
- education: list of {institution, degree, field, start_date (YYYY-MM), end_date (YYYY-MM)}
- certifications: list of {name, issuer, issued_at (YYYY-MM-DD)}
- summary: string (1-2 sentence professional summary)

Rules:
- Only include items explicitly mentioned in the resume text.
- If a section has no data, return an empty list [].
- For proficiency, estimate from context: 0.3=basic, 0.5=intermediate, 0.7=advanced, 0.9=expert.
- Use null for unknown dates, empty string for unknown fields.

Resume text:
{resume_text}

Return ONLY valid JSON:"""


async def parse_resume_to_candidates(
    client: LLMClient,
    resume_text: str,
) -> dict:
    """Parse resume text into structured candidate entities.

    Returns a dict with positions, projects, skills, education, certifications, summary.
    Each value is a list of candidate dicts (or string for summary).
    """
    prompt = RESUME_PARSING_PROMPT.format(resume_text=resume_text[:8000])

    try:
        result = await client.generate(
            messages=[{"role": "user", "content": prompt}],
        )
        content = result.get("content", "")
        # Try to parse JSON from the response
        return _parse_llm_json(content)
    except Exception:
        # If LLM call fails, return empty results
        return _empty_result()


def _parse_llm_json(content: str) -> dict:
    """Extract JSON object from LLM response, handling markdown fences."""
    # Strip markdown code fences if present
    text = content.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first ```json and last ```
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    try:
        data = json.loads(text)
        return _validate_result(data)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        import re
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return _validate_result(data)
            except json.JSONDecodeError:
                pass
    return _empty_result()


def _validate_result(data: dict) -> dict:
    """Ensure the result has all expected keys with correct types."""
    expected = {
        "positions": [],
        "projects": [],
        "skills": [],
        "education": [],
        "certifications": [],
        "summary": "",
    }
    for key in expected:
        if key not in data:
            data[key] = expected[key]
    # Ensure lists are lists
    for key in ("positions", "projects", "skills", "education", "certifications"):
        if not isinstance(data.get(key), list):
            data[key] = []
    if not isinstance(data.get("summary"), str):
        data["summary"] = ""
    return data


def _empty_result() -> dict:
    return {
        "positions": [],
        "projects": [],
        "skills": [],
        "education": [],
        "certifications": [],
        "summary": "",
    }


def mock_parse_resume(resume_text: str) -> dict:
    """Mock parser for testing — returns deterministic structured data."""
    text_lower = resume_text.lower()

    # Simple keyword-based extraction
    positions = []
    projects = []
    skills = []
    education = []
    certifications = []

    # Detect skills
    skill_keywords = {
        "python": ("Python", "Programming", 0.8),
        "javascript": ("JavaScript", "Programming", 0.7),
        "typescript": ("TypeScript", "Programming", 0.7),
        "react": ("React", "Framework", 0.7),
        "fastapi": ("FastAPI", "Framework", 0.7),
        "docker": ("Docker", "Tool", 0.7),
        "kubernetes": ("Kubernetes", "Tool", 0.6),
        "aws": ("AWS", "Cloud", 0.7),
        "sql": ("SQL", "Programming", 0.8),
        "postgresql": ("PostgreSQL", "Tool", 0.7),
        "git": ("Git", "Tool", 0.8),
        "agile": ("Agile", "Soft Skill", 0.6),
        "java": ("Java", "Programming", 0.7),
        "c++": ("C++", "Programming", 0.7),
        "rust": ("Rust", "Programming", 0.6),
        "linux": ("Linux", "Tool", 0.7),
        "mongodb": ("MongoDB", "Tool", 0.6),
        "redis": ("Redis", "Tool", 0.6),
    }
    for keyword, (name, category, prof) in skill_keywords.items():
        if keyword in text_lower:
            skills.append({"name": name, "category": category, "proficiency": prof})

    # Detect education
    edu_keywords = {
        "bachelor": ("BSc", "Computer Science"),
        "b.s.": ("BSc", "Computer Science"),
        "master": ("MSc", "Computer Science"),
        "m.s.": ("MSc", "Computer Science"),
        "phd": ("PhD", "Computer Science"),
        "ph.d": ("PhD", "Computer Science"),
        "mba": ("MBA", "Business"),
    }
    for keyword, (degree, field) in edu_keywords.items():
        if keyword in text_lower:
            # Try to find institution name nearby
            education.append({
                "institution": "University",
                "degree": degree,
                "field": field,
                "start_date": None,
                "end_date": None,
            })

    # Detect positions from company mentions
    company_patterns = [" at ", "worked for ", "employed by ", "company:", "inc.", "llc", "corp", "ltd"]
    # Simple heuristic: look for lines with "experience" or role titles
    for line in resume_text.split("\n"):
        line_lower = line.strip().lower()
        for title in ["engineer", "developer", "manager", "lead", "architect", "analyst", "designer", "scientist"]:
            if title in line_lower and len(line) < 150:
                # Extract what looks like a position
                company = "Company"
                for kw in company_patterns:
                    if kw in line_lower:
                        parts = line.split(kw)
                        if len(parts) > 1:
                            company = parts[1].strip().split(",")[0].strip()
                positions.append({
                    "company": company,
                    "title": line.strip(),
                    "start_date": None,
                    "end_date": None,
                    "description": line.strip(),
                })
                break

    # Generate a simple summary
    skill_names = [s["name"] for s in skills]
    summary = ""
    if skill_names:
        summary = f"Professional with experience in {', '.join(skill_names[:5])}."

    return {
        "positions": positions[:5],
        "projects": projects[:3],
        "skills": skills,
        "education": education[:3],
        "certifications": certifications[:3],
        "summary": summary,
    }
