"""Data models for the Resume Screening & Candidate Evaluation System."""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recommendation(str, Enum):
    STRONG_YES = "Strong Yes"
    YES = "Yes"
    MAYBE = "Maybe"
    NO = "No"


class JobDescription(BaseModel):
    """Parsed job description structure."""
    title: str = ""
    company: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_experience_years: Optional[int] = None
    education_requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    raw_text: str = ""


class ResumeData(BaseModel):
    """Parsed resume structure."""
    candidate_name: str = ""
    email: str = ""
    phone: str = ""
    skills: list[str] = Field(default_factory=list)
    experience_years: Optional[float] = None
    education: list[str] = Field(default_factory=list)
    work_history: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    raw_text: str = ""


class ScoreBreakdown(BaseModel):
    """Detailed scoring breakdown for a candidate."""
    skill_match: float = Field(0, ge=0, le=100, description="Score for skill alignment")
    experience_relevance: float = Field(0, ge=0, le=100, description="Score for experience relevance")
    education_fit: float = Field(0, ge=0, le=100, description="Score for education match")
    role_alignment: float = Field(0, ge=0, le=100, description="Score for overall role fit")
    overall_impression: float = Field(0, ge=0, le=100, description="General impression score")
    weighted_total: float = Field(0, ge=0, le=100, description="Final weighted score")
    reasoning: str = ""


class GapAnalysis(BaseModel):
    """Identified gaps and risks in a candidate's profile."""
    missing_required_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    experience_gaps: list[str] = Field(default_factory=list)
    education_gaps: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW


class CandidateSummary(BaseModel):
    """Concise summary of candidate strengths."""
    top_strengths: list[str] = Field(default_factory=list)
    key_experience: str = ""
    unique_qualifications: list[str] = Field(default_factory=list)
    summary_text: str = ""


class EvaluationResult(BaseModel):
    """Complete evaluation result for a candidate."""
    candidate_name: str = ""
    job_title: str = ""
    scores: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    summary: CandidateSummary = Field(default_factory=CandidateSummary)
    gaps: GapAnalysis = Field(default_factory=GapAnalysis)
    recommendation: Recommendation = Recommendation.MAYBE
    recommendation_reason: str = ""
    shortlisted: bool = False
