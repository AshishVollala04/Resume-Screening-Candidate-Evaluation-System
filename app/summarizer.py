"""Summarizer: generates concise candidate strength summaries."""

from app.llm_client import call_llm_json
from app.models import CandidateSummary

SUMMARY_SYSTEM_PROMPT = """You are an expert recruitment summarizer. Your job is to create a concise, recruiter-friendly summary of a candidate's strengths based on their resume and the target job.

Return a JSON object with these exact keys:
{
  "top_strengths": ["strength 1", "strength 2", "strength 3"],
  "key_experience": "One paragraph summarizing the most relevant experience",
  "unique_qualifications": ["qualification 1", "qualification 2"],
  "summary_text": "A 2-3 sentence executive summary for the recruiter"
}

Guidelines:
- top_strengths: 3-5 most compelling strengths relevant to the role
- key_experience: Focus on experience most relevant to the job description
- unique_qualifications: Certifications, rare skills, or standout achievements
- summary_text: Brief, professional summary a recruiter can scan in 10 seconds

Be positive but honest. Focus on facts from the resume."""


def summarize_candidate(resume_text: str, jd_text: str) -> CandidateSummary:
    """Generate a concise summary of candidate strengths."""
    user_prompt = f"""## Job Description
{jd_text}

## Candidate Resume
{resume_text}

Summarize this candidate's strengths for the recruiter. Return JSON only."""

    result = call_llm_json(SUMMARY_SYSTEM_PROMPT, user_prompt)

    return CandidateSummary(
        top_strengths=result.get("top_strengths", []),
        key_experience=result.get("key_experience", ""),
        unique_qualifications=result.get("unique_qualifications", []),
        summary_text=result.get("summary_text", ""),
    )
