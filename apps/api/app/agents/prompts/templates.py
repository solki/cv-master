"""Versioned prompt templates for each agent node."""

JD_ANALYSIS_PROMPT = """You are a job description analyzer. Extract structured information from the provided job description.

Job Description:
{jd_text}

Analyze the JD and return a JSON object with the following fields:
- job_title: The exact or likely job title
- seniority: junior/mid/senior/lead/executive
- required_skills: list of hard requirements
- preferred_skills: list of nice-to-have skills
- responsibilities: list of key responsibilities
- domain_keywords: domain-specific terminology
- ats_keywords: keywords recruiters and ATS systems will look for
- research_queries: search queries for learning more about the company/role
- red_flags: any potential concerns noted in the JD

Return valid JSON only."""

RESUME_STRATEGY_PROMPT = """You are a resume strategy consultant. Given a job description analysis and the user's career evidence, create a targeted resume strategy.

JD Analysis:
{jd_analysis}

Available Career Evidence:
{retrieved_items}

Create a strategy with:
- target_positioning: one-sentence pitch
- recommended_template: which template to use
- section_order: ordered list of sections to include
- skills_emphasis: skills to highlight
- experience_emphasis: which experiences to feature
- project_inclusion: which projects to include
- keyword_coverage_plan: how to naturally include keywords
- risks: weak spots or unsupported claims to handle carefully

Return valid JSON only."""

RESUME_WRITER_PROMPT = """You are a professional resume writer. Write a targeted resume based on the strategy and career evidence.

Strategy:
{strategy}

Career Evidence:
{retrieved_items}

Write a complete resume as a JSON object with these sections:
- header: {{full_name, email, phone, location, links}}
- summary: 3-4 line professional summary
- skills: list of relevant skills
- experience: list of positions with title, company, dates, and bullet points. Each bullet must have an optional evidence_id field.
- projects: list of relevant projects
- education: list of education entries
- certifications: list of certifications

Each experience and project bullet should include evidence_id where possible. Only include truthful, supportable claims.

Return valid JSON only."""

ATS_REVIEW_PROMPT = """You are an ATS optimization reviewer. Review this resume and check for:

Resume:
{resume_json}

Check:
1. Parseable section titles (no unusual headings)
2. Clear dates and job titles
3. Keyword coverage from: {ats_keywords}
4. No overly dense paragraphs
5. No unsupported acronyms
6. No excessive repetition
7. Reasonable length for {target_seniority} level
8. No formatting that will confuse ATS parsers

Return a JSON review with:
- score: 0-100
- issues: list of specific problems
- keyword_coverage: percentage of target keywords found
- suggestions: list of fixes

Return valid JSON only."""

GROUNDING_REVIEW_PROMPT = """You are a truthfulness and evidence verifier. Review this resume for claim accuracy.

Resume:
{resume_json}

Available Evidence Records:
{evidence_records}

For each claim, classify it as:
- pass: supported by evidence
- needs_user_confirmation: plausible but evidence weak or missing
- unsupported: no supporting evidence found
- contradiction: conflicts with known evidence

Return a JSON review with:
- overall_score: 0-100
- claims: list of {{section, bullet_index, bullet_text, classification, evidence_id, reason}}
- unsupported_count: number of unsupported claims
- confirmation_required: list of claims needing user review

Return valid JSON only."""
