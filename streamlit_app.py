"""Streamlit Web UI for Resume Screening & Candidate Evaluation System."""

import streamlit as st
from app.resume_parser import extract_text_from_bytes
from app.evaluator import evaluate_candidate, evaluate_batch

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Resume Screening & Candidate Evaluation System")
st.markdown("*AI-powered resume screening that scores, summarizes, and identifies gaps*")
st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    shortlist_threshold = st.slider("Shortlist Threshold", 0, 100, 70, 5)
    st.divider()
    st.markdown("""
    **How it works:**
    1. Paste or upload a Job Description
    2. Upload one or more resumes
    3. AI evaluates each candidate
    4. View scores, summaries & gaps
    """)

# --- Job Description Input ---
st.header("1️⃣ Job Description")
jd_input_method = st.radio("Input method:", ["Paste Text", "Upload File"], horizontal=True)

jd_text = ""
if jd_input_method == "Paste Text":
    jd_text = st.text_area(
        "Paste the job description here:",
        height=200,
        placeholder="Enter the full job description including required skills, experience, education..."
    )
else:
    jd_file = st.file_uploader("Upload JD file", type=["pdf", "docx", "txt"], key="jd_upload")
    if jd_file:
        try:
            jd_text = extract_text_from_bytes(jd_file.getvalue(), jd_file.name)
            st.success(f"✅ Extracted {len(jd_text)} characters from {jd_file.name}")
            with st.expander("Preview JD text"):
                st.text(jd_text[:2000])
        except Exception as e:
            st.error(f"❌ Error reading JD: {e}")

# --- Resume Upload ---
st.header("2️⃣ Upload Resumes")
resume_files = st.file_uploader(
    "Upload resume files",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    key="resume_upload",
)

# --- Evaluate Button ---
st.header("3️⃣ Evaluate")

if st.button("🚀 Run Evaluation", type="primary", use_container_width=True):
    if not jd_text.strip():
        st.error("❌ Please provide a job description first.")
    elif not resume_files:
        st.error("❌ Please upload at least one resume.")
    else:
        # Extract all resume texts
        resumes = []
        for f in resume_files:
            try:
                text = extract_text_from_bytes(f.getvalue(), f.name)
                resumes.append((f.name, text))
            except Exception as e:
                st.warning(f"⚠️ Skipping {f.name}: {e}")

        if not resumes:
            st.error("❌ No valid resumes could be processed.")
        else:
            # Run evaluation
            with st.spinner(f"🔍 Evaluating {len(resumes)} candidate(s)..."):
                try:
                    results = evaluate_batch(resumes, jd_text)
                except Exception as e:
                    st.error(f"❌ Evaluation failed: {e}")
                    st.stop()

            # --- Display Results ---
            st.header("4️⃣ Results")

            # Ranking table
            st.subheader("📊 Candidate Ranking")
            ranking_data = []
            for i, r in enumerate(results, 1):
                ranking_data.append({
                    "Rank": i,
                    "Candidate": r.candidate_name,
                    "Score": f"{r.scores.weighted_total:.1f}/100",
                    "Recommendation": r.recommendation.value,
                    "Risk Level": r.gaps.risk_level.value.title(),
                    "Shortlisted": "✅" if r.shortlisted else "❌",
                })
            st.table(ranking_data)

            # Detailed results per candidate
            for i, r in enumerate(results, 1):
                shortlist_emoji = "✅" if r.shortlisted else "❌"
                with st.expander(f"**#{i} — {r.candidate_name}** | Score: {r.scores.weighted_total:.1f} | {r.recommendation.value} {shortlist_emoji}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 📈 Score Breakdown")
                        st.progress(r.scores.skill_match / 100, text=f"Skill Match: {r.scores.skill_match}")
                        st.progress(r.scores.experience_relevance / 100, text=f"Experience: {r.scores.experience_relevance}")
                        st.progress(r.scores.education_fit / 100, text=f"Education: {r.scores.education_fit}")
                        st.progress(r.scores.role_alignment / 100, text=f"Role Alignment: {r.scores.role_alignment}")
                        st.progress(r.scores.overall_impression / 100, text=f"Overall: {r.scores.overall_impression}")
                        st.metric("Weighted Total", f"{r.scores.weighted_total:.1f}/100")
                        st.caption(f"**Reasoning:** {r.scores.reasoning}")

                    with col2:
                        st.markdown("### 💪 Strengths Summary")
                        st.write(r.summary.summary_text)
                        if r.summary.top_strengths:
                            st.markdown("**Top Strengths:**")
                            for s in r.summary.top_strengths:
                                st.markdown(f"- ✅ {s}")
                        if r.summary.unique_qualifications:
                            st.markdown("**Unique Qualifications:**")
                            for q in r.summary.unique_qualifications:
                                st.markdown(f"- 🌟 {q}")

                    st.markdown("---")
                    st.markdown("### ⚠️ Gaps & Risks")
                    gap_col1, gap_col2 = st.columns(2)

                    with gap_col1:
                        if r.gaps.missing_required_skills:
                            st.markdown("**Missing Required Skills:**")
                            for s in r.gaps.missing_required_skills:
                                st.markdown(f"- 🔴 {s}")
                        if r.gaps.missing_preferred_skills:
                            st.markdown("**Missing Preferred Skills:**")
                            for s in r.gaps.missing_preferred_skills:
                                st.markdown(f"- 🟡 {s}")

                    with gap_col2:
                        if r.gaps.experience_gaps:
                            st.markdown("**Experience Gaps:**")
                            for g in r.gaps.experience_gaps:
                                st.markdown(f"- 📋 {g}")
                        if r.gaps.risk_flags:
                            st.markdown("**Risk Flags:**")
                            for f in r.gaps.risk_flags:
                                st.markdown(f"- 🚩 {f}")

                    st.markdown("---")
                    rec_color = {
                        "Strong Yes": "green", "Yes": "blue",
                        "Maybe": "orange", "No": "red"
                    }.get(r.recommendation.value, "gray")
                    st.markdown(f"### 🎯 Recommendation: :{rec_color}[{r.recommendation.value}]")
                    st.write(r.recommendation_reason)
