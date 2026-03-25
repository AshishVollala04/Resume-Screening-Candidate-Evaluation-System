"""Scorer: LLM-based candidate scoring against job descriptions."""

from app.llm_client import call_llm_json
from app.config import SCORE_WEIGHTS
from app.models import ScoreBreakdown

SCORING_SYSTEM_PROMPT = """You are an expert recruitment evaluator. Your job is to score a candidate's resume against a job description.

You must return a JSON object with these exact keys:
{
  "skill_match": <0-100>,
  "experience_relevance": <0-100>,
  "education_fit": <0-100>,
  "role_alignment": <0-100>,
  "overall_impression": <0-100>,
  "reasoning": "<2-3 sentence explanation of the scores>"
}

Scoring guidelines:
- skill_match: How well do the candidate's skills match required and preferred skills? (0=no match, 100=perfect match)
- experience_relevance: How relevant is their work experience to this role? (0=irrelevant, 100=highly relevant)
- education_fit: How well does their education match requirements? (0=no match, 100=exceeds requirements)
- role_alignment: Overall fit for the role considering responsibilities and culture? (0=poor fit, 100=ideal fit)
- overall_impression: General impression of the candidate's profile quality? (0=weak, 100=exceptional)

Be objective, fair, and consistent. Evaluate based solely on qualifications and fit."""


def score_candidate(resume_text: str, jd_text: str) -> ScoreBreakdown:
    """Score a candidate's resume against a job description using LLM."""
    user_prompt = f"""## Job Description
{jd_text}

## Candidate Resume
{resume_text}

Score this candidate against the job description. Return JSON only."""

    result = call_llm_json(SCORING_SYSTEM_PROMPT, user_prompt)

    # Calculate weighted total
    weighted_total = sum(
        result.get(key, 0) * weight
        for key, weight in SCORE_WEIGHTS.items()
    )

    return ScoreBreakdown(
        skill_match=result.get("skill_match", 0),
        experience_relevance=result.get("experience_relevance", 0),
        education_fit=result.get("education_fit", 0),
        role_alignment=result.get("role_alignment", 0),
        overall_impression=result.get("overall_impression", 0),
        weighted_total=round(weighted_total, 1),
        reasoning=result.get("reasoning", ""),
    )
