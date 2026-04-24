import streamlit as st
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase1_resume.resume_parser import parse_resume
from phase2_video.video_evaluator import evaluate_video
from phase3_ranking.ranker import run_ranking, load_all_candidates, rank_candidates

st.set_page_config(
    page_title="AI Candidate Evaluator",
    page_icon="🤖",
    layout="wide"
)

st.sidebar.title("🤖 AI Candidate Evaluator")
page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "📄 Evaluate Candidate",
    "🏆 All Rankings",
    "📊 Generate Report"
])

# --- HOME PAGE ---
if page == "🏠 Home":
    st.title("AI-Powered Candidate Evaluation System")
    st.markdown("### Automate your hiring process with AI")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📄 **Phase 1**\nUpload resume → AI extracts skills, scores, strengths")
    with col2:
        st.info("🎥 **Phase 2**\nUpload video → Whisper transcribes → AI scores communication")
    with col3:
        st.info("🏆 **Phase 3**\nAll candidates ranked → Download PDF report")

    st.markdown("---")
    st.markdown("**Built with:** Python · Groq LLaMA · Whisper · scikit-learn · Streamlit")

# --- EVALUATE PAGE ---
elif page == "📄 Evaluate Candidate":
    st.title("📄 Evaluate a Candidate")

    candidate_name = st.text_input("Candidate Name (used as ID)", placeholder="e.g. Jay Patel")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Resume Upload")
        resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

    with col2:
        st.subheader("Video Upload")
        video_file = st.file_uploader("Upload Interview Video", type=["mp4", "avi", "mov"])

    if st.button("🚀 Evaluate Candidate", use_container_width=True):
        if not candidate_name:
            st.error("Please enter candidate name!")
        elif not resume_file:
            st.error("Please upload a resume PDF!")
        else:
            candidate_id = candidate_name.strip().replace(" ", "_")

            # Save resume
            resume_path = f"data/resumes/{candidate_id}.pdf"
            with open(resume_path, "wb") as f:
                f.write(resume_file.read())

            # Phase 1
            with st.spinner("🔍 Analyzing resume with AI..."):
                resume_result = parse_resume(resume_path, candidate_id=candidate_id)

            if resume_result:
                st.success("✅ Resume analyzed!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Resume Score", f"{resume_result['overall_resume_score']}/100")
                with col2:
                    st.metric("Experience", f"{resume_result['experience_years']} years")
                with col3:
                    st.metric("Skills Found", len(resume_result['skills']))

                with st.expander("📋 Full Resume Analysis"):
                    st.json(resume_result)

            # Phase 2
            if video_file:
                video_path = f"data/videos/{candidate_id}.mp4"
                with open(video_path, "wb") as f:
                    f.write(video_file.read())

                with st.spinner("🎥 Transcribing and analyzing video..."):
                    video_result = evaluate_video(video_path, candidate_id)

                if video_result:
                    st.success("✅ Video analyzed!")
                    with st.expander("🎥 Video Evaluation"):
                        st.json(video_result)
            else:
                st.warning("No video uploaded - only resume will be scored")

            st.balloons()
            st.success(f"✅ {candidate_name} evaluation complete! Go to Rankings to see results.")

# --- RANKINGS PAGE ---
elif page == "🏆 All Rankings":
    st.title("🏆 Candidate Rankings")

    candidates = load_all_candidates()

    if not candidates:
        st.warning("No candidates evaluated yet. Go to Evaluate Candidate first!")
    else:
        ranked = rank_candidates(candidates)

        for candidate in ranked:
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                with col1:
                    st.markdown(f"### #{candidate['rank']}")
                with col2:
                    st.markdown(f"**{candidate['name']}**")
                    st.caption(candidate['email'])
                with col3:
                    st.metric("Final Score", f"{candidate['final_score']}/100")
                with col4:
                    st.metric("Resume Score", f"{candidate['resume_score']}/100")
                st.markdown(f"*{candidate['summary']}*")
                st.divider()

# --- REPORT PAGE ---
elif page == "📊 Generate Report":
    st.title("📊 Generate PDF Report")

    candidates = load_all_candidates()

    if not candidates:
        st.warning("No candidates found. Evaluate some candidates first!")
    else:
        st.info(f"Ready to generate report for {len(candidates)} candidate(s)")

        if st.button("📥 Generate & Download Report", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                from phase3_ranking.ranker import generate_pdf_report, rank_candidates
                ranked = rank_candidates(candidates)
                report_path = generate_pdf_report(ranked)

            with open(report_path, "rb") as f:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=f,
                    file_name="candidate_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            st.success("Report generated!")
