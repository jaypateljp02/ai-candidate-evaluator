"""
AI Candidate Evaluator — Main Streamlit Application
A comprehensive AI-powered candidate evaluation system with resume parsing,
video interview analysis, ranking, and PDF report generation.
"""

import streamlit as st
import json
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))



from phase1_resume.resume_parser import parse_resume
from phase2_video.video_evaluator import evaluate_video
from phase3_ranking.ranker import run_ranking, load_all_candidates, rank_candidates, generate_pdf_report
from phase3_ranking.clustering import get_cluster_summary, TIER_EMOJIS, TIER_COLORS

# ──────────────────────────────────────────────
# Page Config & Custom CSS
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="AI Candidate Evaluator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    /* Phase cards */
    .phase-card {
        background: linear-gradient(135deg, rgba(52,152,219,0.15) 0%, rgba(41,128,185,0.1) 100%);
        border: 1px solid rgba(52,152,219,0.3);
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        min-height: 200px;
    }
    .phase-card h3 {
        color: #3498db;
        margin-bottom: 12px;
    }

    /* Score badge */
    .score-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.2em;
        color: white;
        text-align: center;
    }
    .score-high { background: linear-gradient(135deg, #27ae60, #2ecc71); }
    .score-mid { background: linear-gradient(135deg, #f39c12, #e67e22); }
    .score-low { background: linear-gradient(135deg, #e74c3c, #c0392b); }

    /* Rank card */
    .rank-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .rank-card:hover {
        border-color: rgba(52,152,219,0.5);
        box-shadow: 0 4px 20px rgba(52,152,219,0.15);
    }

    /* Title styling */
    .hero-title {
        font-size: 2.5em;
        font-weight: 800;
        background: linear-gradient(135deg, #3498db, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.6);
        text-align: center;
        font-size: 1.1em;
        margin-bottom: 30px;
    }

    /* Tech badge */
    .tech-badge {
        display: inline-block;
        background: rgba(52,152,219,0.15);
        border: 1px solid rgba(52,152,219,0.3);
        color: #3498db;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        margin: 3px;
    }

    /* Divider */
    .custom-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(52,152,219,0.3), transparent);
        margin: 30px 0;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Ensure directories exist
# ──────────────────────────────────────────────

os.makedirs("data/resumes", exist_ok=True)
os.makedirs("data/videos", exist_ok=True)
os.makedirs("output/reports", exist_ok=True)


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def get_score_class(score):
    """Return CSS class based on score value."""
    if score >= 70:
        return "score-high"
    elif score >= 40:
        return "score-mid"
    else:
        return "score-low"


def count_candidates():
    """Count evaluated candidates."""
    count = 0
    if os.path.exists("output"):
        for f in os.listdir("output"):
            if f.endswith("_resume.json"):
                count += 1
    return count


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🤖 AI Candidate Evaluator")
    st.markdown("---")

    page = st.radio("Navigate", [
        "🏠 Home",
        "📄 Evaluate Candidate",
        "🏆 All Rankings",
        "📊 Generate Report"
    ], label_visibility="collapsed")

    st.markdown("---")

    # Stats in sidebar
    candidate_count = count_candidates()
    st.markdown(f"**📊 Candidates Evaluated:** `{candidate_count}`")

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color: rgba(255,255,255,0.4); font-size:0.8em;'>"
        "Built with Groq AI + Whisper<br>by Jay Patel"
        "</div>",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════

if page == "🏠 Home":
    st.markdown('<div class="hero-title">AI Candidate Evaluator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Automate your hiring pipeline with AI-powered resume analysis, video interview evaluation, and intelligent candidate ranking</div>', unsafe_allow_html=True)
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2.5em; font-weight: 800; color: #3498db;">{count_candidates()}</div>
            <div style="color: rgba(255,255,255,0.6); margin-top: 5px;">Total Candidates Evaluated</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_score = 0
        if count_candidates() > 0:
            candidates = load_all_candidates()
            if candidates:
                ranked = rank_candidates(candidates)
                avg_score = int(sum(c['final_score'] for c in ranked) / len(ranked))
                
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2.5em; font-weight: 800; color: #2ecc71;">{avg_score}<span style="font-size: 0.5em;">/100</span></div>
            <div style="color: rgba(255,255,255,0.6); margin-top: 5px;">Average Candidate Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="phase-card">
            <h3>📄 Phase 1</h3>
            <p style="font-size: 2em; margin: 10px 0;">📝</p>
            <p><strong>Resume Analysis</strong></p>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.9em;">
                Upload PDF resume → AI extracts skills, experience, education → Generates score out of 100
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="phase-card">
            <h3>🎥 Phase 2</h3>
            <p style="font-size: 2em; margin: 10px 0;">🎤</p>
            <p><strong>Video Interview</strong></p>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.9em;">
                Upload video → Whisper transcribes speech → AI evaluates communication skills
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="phase-card">
            <h3>🏆 Phase 3</h3>
            <p style="font-size: 2em; margin: 10px 0;">📊</p>
            <p><strong>Ranking & Reports</strong></p>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.9em;">
                Weighted scoring → All candidates ranked → Professional PDF report download
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Scoring info
    st.markdown("### 📐 Scoring System")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size: 2em; color: #3498db;">60%</div>
            <div style="color: rgba(255,255,255,0.7);">Resume Score</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size: 2em; color: #9b59b6;">40%</div>
            <div style="color: rgba(255,255,255,0.7);">Video Score</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size: 2em; color: #2ecc71;">100%</div>
            <div style="color: rgba(255,255,255,0.7);">Final Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Tech stack
    st.markdown("### 🛠️ Tech Stack")
    techs = ["Python", "Streamlit", "Groq LLaMA 3.3", "OpenAI Whisper", "pdfplumber", "FFmpeg", "fpdf2", "pandas", "scikit-learn"]
    badges_html = " ".join([f'<span class="tech-badge">{t}</span>' for t in techs])
    st.markdown(f'<div style="text-align:center;">{badges_html}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# EVALUATE CANDIDATE PAGE
# ══════════════════════════════════════════════

elif page == "📄 Evaluate Candidate":
    st.markdown("# 📄 Evaluate a Candidate")
    st.markdown("Upload a resume (required) and optionally a video interview for AI-powered analysis.")
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    candidate_name = st.text_input(
        "👤 Candidate Name",
        placeholder="e.g. Jay Patel",
        help="Used as the candidate's unique identifier"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>📄 Resume Upload</h4>
            <p style="color: rgba(255,255,255,0.5);">Supported: PDF files</p>
        </div>
        """, unsafe_allow_html=True)
        resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"], label_visibility="collapsed")

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>🎥 Video Upload (Optional)</h4>
            <p style="color: rgba(255,255,255,0.5);">Supported: MP4, AVI, MOV</p>
        </div>
        """, unsafe_allow_html=True)
        video_file = st.file_uploader("Upload Interview Video", type=["mp4", "avi", "mov"], label_visibility="collapsed")

    st.markdown("")

    if st.button("🚀 Evaluate Candidate", use_container_width=True, type="primary"):
        if not candidate_name:
            st.error("⚠️ Please enter candidate name!")
        elif not resume_file:
            st.error("⚠️ Please upload a resume PDF!")
        else:
            candidate_id = candidate_name.strip().replace(" ", "_")

            # Save resume file
            resume_path = f"data/resumes/{candidate_id}.pdf"
            with open(resume_path, "wb") as f:
                f.write(resume_file.read())

            # ── Phase 1: Resume Analysis ──
            with st.spinner("🔍 Phase 1: Analyzing resume with AI..."):
                resume_result = parse_resume(resume_path, candidate_id=candidate_id)

            if resume_result:
                st.success("✅ Resume analyzed successfully!")

                # Score display
                score = resume_result.get('overall_resume_score', 0)
                score_class = get_score_class(score)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align:center;">
                        <div style="color: rgba(255,255,255,0.5); font-size:0.9em;">Resume Score</div>
                        <div class="score-badge {score_class}" style="margin-top:8px;">{score}/100</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align:center;">
                        <div style="color: rgba(255,255,255,0.5); font-size:0.9em;">Experience</div>
                        <div style="font-size:1.8em; font-weight:700; color: #3498db;">{resume_result.get('experience_years', 0)} yrs</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align:center;">
                        <div style="color: rgba(255,255,255,0.5); font-size:0.9em;">Skills Found</div>
                        <div style="font-size:1.8em; font-weight:700; color: #2ecc71;">{len(resume_result.get('skills', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("📋 Full Resume Analysis", expanded=False):
                    st.json(resume_result)
            else:
                st.error("❌ Resume analysis failed. Please check the file and try again.")

            # ── Phase 2: Video Analysis ──
            if video_file:
                video_path = f"data/videos/{candidate_id}.mp4"
                with open(video_path, "wb") as f:
                    f.write(video_file.read())

                with st.spinner("🎥 Phase 2: Transcribing and analyzing video..."):
                    video_result = evaluate_video(video_path, candidate_id)

                if video_result:
                    st.success("✅ Video analyzed successfully!")

                    eval_data = video_result.get("evaluation", {})
                    comm_score = eval_data.get("communication_score", 0)
                    comm_class = get_score_class(comm_score)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card" style="text-align:center;">
                            <div style="color: rgba(255,255,255,0.5); font-size:0.9em;">Communication Score</div>
                            <div class="score-badge {comm_class}" style="margin-top:8px;">{comm_score}/100</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card" style="text-align:center;">
                            <div style="color: rgba(255,255,255,0.5); font-size:0.9em;">Confidence</div>
                            <div style="font-size:1.5em; font-weight:700; color: #e67e22;">{eval_data.get('confidence', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card" style="text-align:center;">
                            <div style="color: rgba(255,255,255,0.5); font-size:0.9em;">Clarity</div>
                            <div style="font-size:1.5em; font-weight:700; color: #9b59b6;">{eval_data.get('clarity', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with st.expander("🎥 Full Video Evaluation", expanded=False):
                        st.json(video_result)
            else:
                st.info("💡 No video uploaded — only resume will be scored. Video interview adds 40% to the final score.")

            st.balloons()
            st.success(f"🎉 {candidate_name} evaluation complete! Go to **Rankings** to see results.")


# ══════════════════════════════════════════════
# RANKINGS PAGE
# ══════════════════════════════════════════════

elif page == "🏆 All Rankings":
    st.markdown("# 🏆 Candidate Rankings")
    st.markdown("All evaluated candidates ranked by composite AI score with ML-based tier classification.")
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    candidates = load_all_candidates()

    if not candidates:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding: 40px;">
            <div style="font-size: 3em;">📭</div>
            <h3>No Candidates Yet</h3>
            <p style="color: rgba(255,255,255,0.5);">Go to <strong>Evaluate Candidate</strong> to analyze your first resume!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        ranked = rank_candidates(candidates)

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div style="color: rgba(255,255,255,0.5);">Total Candidates</div>
                <div style="font-size: 2em; font-weight: 700; color: #3498db;">{len(ranked)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            avg_score = round(sum(c['final_score'] for c in ranked) / len(ranked), 1) if ranked else 0
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div style="color: rgba(255,255,255,0.5);">Average Score</div>
                <div style="font-size: 2em; font-weight: 700; color: #f39c12;">{avg_score}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            top_score = ranked[0]['final_score'] if ranked else 0
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div style="color: rgba(255,255,255,0.5);">Top Score</div>
                <div style="font-size: 2em; font-weight: 700; color: #2ecc71;">{top_score}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            # Tier distribution
            tier_counts = {}
            for c in ranked:
                t = c.get('tier', 'N/A')
                tier_counts[t] = tier_counts.get(t, 0) + 1
            tier_text = " · ".join([f"{TIER_EMOJIS.get(t, '⚪')}{v}" for t, v in tier_counts.items()])
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div style="color: rgba(255,255,255,0.5);">Tier Distribution</div>
                <div style="font-size: 1.2em; font-weight: 700; margin-top: 8px;">{tier_text}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Candidate cards with tier badges, keywords, sentiment
        for candidate in ranked:
            score_class = get_score_class(candidate['final_score'])
            tier = candidate.get('tier', 'N/A')
            tier_emoji = TIER_EMOJIS.get(tier, '⚪')
            tier_color = TIER_COLORS.get(tier, '#888')

            medal = ""
            if candidate['rank'] == 1: medal = "🥇"
            elif candidate['rank'] == 2: medal = "🥈"
            elif candidate['rank'] == 3: medal = "🥉"

            # Keywords and sentiment
            keywords = candidate.get('keywords', [])
            keywords_html = " ".join([f'<span class="tech-badge">{k}</span>' for k in keywords[:6]]) if keywords else '<span style="color:rgba(255,255,255,0.3);">No keywords</span>'
            
            sent_label = candidate.get('sentiment_label', 'No Data')
            sent_emoji = "😊" if sent_label == "Positive" else "😐" if sent_label == "Neutral" else "😟" if sent_label == "Negative" else "—"

            st.markdown(f"""
            <div class="rank-card">
                <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
                    <div style="font-size: 2em; font-weight: 800; color: #3498db; min-width: 60px;">
                        {medal} #{candidate['rank']}
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <div style="font-size: 1.2em; font-weight: 600;">{candidate['name']}
                            <span style="background:{tier_color}; color:white; padding:2px 10px; border-radius:20px; font-size:0.7em; margin-left:8px;">{tier_emoji} {tier}</span>
                        </div>
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.9em;">{candidate['email']} · {candidate['experience_years']} yrs exp · {candidate['skills_count']} skills · Sentiment: {sent_emoji} {sent_label}</div>
                    </div>
                    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                        <div class="score-badge {score_class}">Final: {candidate['final_score']}</div>
                        <div style="text-align:center; padding: 5px 10px;">
                            <div style="color: rgba(255,255,255,0.4); font-size:0.75em;">Resume</div>
                            <div style="font-weight:600;">{candidate['resume_score']}</div>
                        </div>
                        <div style="text-align:center; padding: 5px 10px;">
                            <div style="color: rgba(255,255,255,0.4); font-size:0.75em;">Video</div>
                            <div style="font-weight:600;">{candidate['video_score']}</div>
                        </div>
                    </div>
                </div>
                <div style="margin-top: 10px;">{keywords_html}</div>
                <div style="margin-top: 8px; color: rgba(255,255,255,0.6); font-size: 0.9em; font-style: italic;">
                    {candidate['summary']}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# REPORT PAGE
# ══════════════════════════════════════════════

elif page == "📊 Generate Report":
    st.markdown("# 📊 Generate PDF Report")
    st.markdown("Download a professionally formatted evaluation report for all candidates.")
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    candidates = load_all_candidates()

    if not candidates:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding: 40px;">
            <div style="font-size: 3em;">📭</div>
            <h3>No Candidates Found</h3>
            <p style="color: rgba(255,255,255,0.5);">Evaluate some candidates first, then come back to generate a report.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 2.5em;">📋</div>
                <div>
                    <div style="font-size: 1.2em; font-weight: 600;">Report Ready</div>
                    <div style="color: rgba(255,255,255,0.5);">
                        {len(candidates)} candidate(s) will be included in the report
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # Report contents preview
        with st.expander("📝 What's in the report?"):
            st.markdown("""
            The PDF report includes:
            - **Summary Table** — All candidates ranked with scores and ML tier classification
            - **Cluster Analysis** — K-Means grouping into Strong Hire / Potential / Needs Review
            - **Detailed Profiles** — Per-candidate breakdown with:
                - Resume score, video score, and final composite score
                - Top keywords extracted via TF-IDF (NLP)
                - Sentiment analysis of video transcript (VADER)
                - Skills, strengths, and areas for improvement
                - Communication assessment and AI-generated summary
            """)

        if st.button("📥 Generate & Download Report", use_container_width=True, type="primary"):
            with st.spinner("📄 Generating professional PDF report..."):
                ranked = rank_candidates(candidates)
                report_path = generate_pdf_report(ranked)

            if report_path and os.path.exists(report_path):
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=f,
                        file_name="candidate_evaluation_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success("✅ Report generated successfully!")
            else:
                st.error("❌ Error generating report. Please try again.")
