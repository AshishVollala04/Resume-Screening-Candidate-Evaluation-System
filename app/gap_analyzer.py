"""Gap Analyzer: identifies missing skills, experience gaps, and risk flags."""

from app.llm_client import call_llm_json
from app.models import GapAnalysis, RiskLevel

GAP_ANALYSIS_SYSTEM_PROMPT = """You are an expert recruitment analyst. Your job is to identify gaps and risks in a candidate's profile when compared to a job description.

Return a JSON object with these exact keys:
{
  "missing_required_skills": ["skill1", "skill2"],
  "missing_preferred_skills": ["skill1"],
  "experience_gaps": ["gap description 1"],
  "education_gaps": ["gap description 1"],
  "risk_flags": ["risk description 1"],
  "risk_level": "low" | "medium" | "high"
}

Guidelines:
- missing_required_skills: Skills explicitly required in the JD that are absent from the resume
- missing_preferred_skills: Nice-to-have skills from the JD not found in the resume
- experience_gaps: Areas where the candidate lacks relevant experience (e.g., "No experience with cloud platforms")
- education_gaps: Education requirements not met (e.g., "JD requires Master's, candidate has Bachelor's")
- risk_flags: Any concerns like career gaps, job hopping, overqualification, or misalignment
- risk_level: "low" (minor gaps), "medium" (notable gaps), "high" (critical mismatches)

Be thorough but fair. Only flag genuine gaps, not minor differences."""


def analyze_gaps(resume_text: str, jd_text: str) -> GapAnalysis:
    """Analyze gaps between a candidate's resume and job description."""
    user_prompt = f"""## Job Description
{jd_text}

## Candidate Resume
{resume_text}

Identify all gaps and risks. Return JSON only."""

    result = call_llm_json(GAP_ANALYSIS_SYSTEM_PROMPT, user_prompt)

    risk_level_str = result.get("risk_level", "low").lower()
    risk_level_map = {"low": RiskLevel.LOW, "medium": RiskLevel.MEDIUM, "high": RiskLevel.HIGH}

    return GapAnalysis(
        missing_required_skills=result.get("missing_required_skills", []),
        missing_preferred_skills=result.get("missing_preferred_skills", []),
        experience_gaps=result.get("experience_gaps", []),
        education_gaps=result.get("education_gaps", []),
        risk_flags=result.get("risk_flags", []),
        risk_level=risk_level_map.get(risk_level_str, RiskLevel.LOW),
    )
