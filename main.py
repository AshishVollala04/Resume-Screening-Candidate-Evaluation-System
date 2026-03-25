"""CLI entry point for Resume Screening & Candidate Evaluation System."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.resume_parser import extract_text
from app.evaluator import evaluate_candidate, evaluate_batch


def print_result(result):
    """Print a single evaluation result to console."""
    print(f"\n{'='*60}")
    print(f"CANDIDATE: {result.candidate_name}")
    print(f"{'='*60}")

    print(f"\n📈 SCORES (Weighted Total: {result.scores.weighted_total:.1f}/100)")
    print(f"  Skill Match:        {result.scores.skill_match}/100")
    print(f"  Experience:         {result.scores.experience_relevance}/100")
    print(f"  Education:          {result.scores.education_fit}/100")
    print(f"  Role Alignment:     {result.scores.role_alignment}/100")
    print(f"  Overall Impression: {result.scores.overall_impression}/100")
    print(f"  Reasoning: {result.scores.reasoning}")

    print(f"\n💪 SUMMARY")
    print(f"  {result.summary.summary_text}")
    if result.summary.top_strengths:
        print(f"  Top Strengths: {', '.join(result.summary.top_strengths)}")

    print(f"\n⚠️  GAPS & RISKS (Risk Level: {result.gaps.risk_level.value})")
    if result.gaps.missing_required_skills:
        print(f"  Missing Required: {', '.join(result.gaps.missing_required_skills)}")
    if result.gaps.missing_preferred_skills:
        print(f"  Missing Preferred: {', '.join(result.gaps.missing_preferred_skills)}")
    if result.gaps.experience_gaps:
        print(f"  Experience Gaps: {', '.join(result.gaps.experience_gaps)}")
    if result.gaps.risk_flags:
        print(f"  Risk Flags: {', '.join(result.gaps.risk_flags)}")

    print(f"\n🎯 RECOMMENDATION: {result.recommendation.value}")
    print(f"  {result.recommendation_reason}")
    print(f"  Shortlisted: {'YES ✅' if result.shortlisted else 'NO ❌'}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <jd_file> <resume_file1> [resume_file2] ...")
        print("\nExample:")
        print("  python main.py sample_data/sample_jd.txt sample_data/resume_strong.txt")
        sys.exit(1)

    jd_path = sys.argv[1]
    resume_paths = sys.argv[2:]

    # Read JD
    print("📋 Reading job description...")
    jd_text = extract_text(jd_path)

    if len(resume_paths) == 1:
        # Single candidate
        print(f"📄 Reading resume: {resume_paths[0]}")
        resume_text = extract_text(resume_paths[0])
        print("🔍 Evaluating candidate...")
        result = evaluate_candidate(resume_text, jd_text)
        result.candidate_name = os.path.basename(resume_paths[0])
        print_result(result)
    else:
        # Batch evaluation
        resumes = []
        for path in resume_paths:
            print(f"📄 Reading resume: {path}")
            text = extract_text(path)
            resumes.append((os.path.basename(path), text))

        print(f"\n🔍 Evaluating {len(resumes)} candidates...")
        results = evaluate_batch(resumes, jd_text)

        print(f"\n{'='*60}")
        print("📊 CANDIDATE RANKING")
        print(f"{'='*60}")
        for i, r in enumerate(results, 1):
            shortlist = "✅" if r.shortlisted else "❌"
            print(f"  #{i} | {r.candidate_name:<30} | Score: {r.scores.weighted_total:>5.1f} | {r.recommendation.value:<12} | {shortlist}")

        for r in results:
            print_result(r)


if __name__ == "__main__":
    main()
