"""Evaluator: Agentic orchestrator that runs the full candidate evaluation pipeline."""

from app.models import EvaluationResult, Recommendation
from app.config import SHORTLIST_THRESHOLD
from app.scorer import score_candidate
from app.summarizer import summarize_candidate
from app.gap_analyzer import analyze_gaps
from app.llm_client import call_llm


RECOMMENDATION_SYSTEM_PROMPT = """You are a senior recruitment decision advisor. Based on the candidate's scores, strengths, and gaps, provide a final hiring recommendation.

Return ONLY one of these values: "Strong Yes", "Yes", "Maybe", "No"
Followed by a pipe character | and a one-sentence reason.

Format: <recommendation>|<reason>

Guidelines:
- "Strong Yes": Weighted score >= 80, minimal gaps, strong alignment
- "Yes": Weighted score >= 70, acceptable gaps, good alignment
- "Maybe": Weighted score 50-69, some concerns but potential
- "No": Weighted score < 50, significant gaps or mismatches"""


def evaluate_candidate(resume_text: str, jd_text: str) -> EvaluationResult:
    """Run the full evaluation pipeline for a single candidate.
    
    This is the main agentic workflow that orchestrates:
    1. Scoring the resume against the JD
    2. Summarizing candidate strengths
    3. Analyzing gaps and risks
    4. Making a final recommendation
    """
    # Step 1: Score the candidate
    scores = score_candidate(resume_text, jd_text)

    # Step 2: Summarize strengths
    summary = summarize_candidate(resume_text, jd_text)

    # Step 3: Analyze gaps
    gaps = analyze_gaps(resume_text, jd_text)

    # Step 4: Generate recommendation
    recommendation, reason = _get_recommendation(scores, summary, gaps)

    # Step 5: Determine shortlist status
    shortlisted = scores.weighted_total >= SHORTLIST_THRESHOLD

    return EvaluationResult(
        candidate_name=summary.summary_text.split(",")[0] if summary.summary_text else "Unknown",
        job_title="",
        scores=scores,
        summary=summary,
        gaps=gaps,
        recommendation=recommendation,
        recommendation_reason=reason,
        shortlisted=shortlisted,
    )


def _get_recommendation(scores, summary, gaps) -> tuple[Recommendation, str]:
    """Get a final recommendation from the LLM based on all evaluation data."""
    user_prompt = f"""## Evaluation Data

Weighted Score: {scores.weighted_total}/100
Score Breakdown:
- Skill Match: {scores.skill_match}/100
- Experience Relevance: {scores.experience_relevance}/100
- Education Fit: {scores.education_fit}/100
- Role Alignment: {scores.role_alignment}/100
- Overall Impression: {scores.overall_impression}/100
Scoring Reasoning: {scores.reasoning}

Top Strengths: {', '.join(summary.top_strengths)}
Summary: {summary.summary_text}

Missing Required Skills: {', '.join(gaps.missing_required_skills) or 'None'}
Missing Preferred Skills: {', '.join(gaps.missing_preferred_skills) or 'None'}
Experience Gaps: {', '.join(gaps.experience_gaps) or 'None'}
Risk Flags: {', '.join(gaps.risk_flags) or 'None'}
Risk Level: {gaps.risk_level.value}

Provide your recommendation."""

    response = call_llm(RECOMMENDATION_SYSTEM_PROMPT, user_prompt)

    # Parse response
    recommendation_map = {
        "Strong Yes": Recommendation.STRONG_YES,
        "Yes": Recommendation.YES,
        "Maybe": Recommendation.MAYBE,
        "No": Recommendation.NO,
    }

    parts = response.strip().split("|", 1)
    rec_text = parts[0].strip()
    reason = parts[1].strip() if len(parts) > 1 else response.strip()

    recommendation = recommendation_map.get(rec_text, Recommendation.MAYBE)
    return recommendation, reason


def evaluate_batch(resumes: list[tuple[str, str]], jd_text: str) -> list[EvaluationResult]:
    """Evaluate multiple candidates and return ranked results.
    
    Args:
        resumes: List of (candidate_name, resume_text) tuples
        jd_text: Job description text
    
    Returns:
        List of EvaluationResult sorted by weighted score (descending)
    """
    results = []
    for name, resume_text in resumes:
        result = evaluate_candidate(resume_text, jd_text)
        result.candidate_name = name
        results.append(result)

    # Sort by score descending
    results.sort(key=lambda r: r.scores.weighted_total, reverse=True)
    return results
