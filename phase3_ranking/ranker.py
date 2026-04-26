"""
Phase 3 — Candidate Ranking & PDF Report Generation
Loads all evaluated candidates, calculates weighted final scores,
ranks them, and generates professional PDF reports.
"""

import json
import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime


# ──────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────

def load_all_candidates(output_dir="output"):
    """Load all evaluated candidates from JSON output files.

    Scans the output directory for *_resume.json files and optionally
    matches them with corresponding *_video.json files.

    Returns:
        dict: candidate_id → { "resume": {...}, "video": {...} or None }
    """
    candidates = {}

    if not os.path.exists(output_dir):
        print("⚠️ Output directory not found")
        return candidates

    for file in os.listdir(output_dir):
        if file.endswith("_resume.json"):
            candidate_id = file.replace("_resume.json", "")
            resume_path = os.path.join(output_dir, file)
            video_path = os.path.join(output_dir, f"{candidate_id}_video.json")

            try:
                with open(resume_path, encoding="utf-8") as f:
                    resume_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error loading {resume_path}: {e}")
                continue

            video_data = None
            if os.path.exists(video_path):
                try:
                    with open(video_path, encoding="utf-8") as f:
                        video_data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"⚠️ Error loading {video_path}: {e}")

            candidates[candidate_id] = {
                "resume": resume_data,
                "video": video_data
            }

    print(f"📊 Loaded {len(candidates)} candidate(s)")
    return candidates


# ──────────────────────────────────────────────
# Scoring
# ──────────────────────────────────────────────

def calculate_final_score(resume_data, video_data):
    """Calculate weighted final score from resume and video evaluations.

    Weights: Resume 60%, Video 40% (if video exists)
    Falls back to resume-only score if no video.
    """
    resume_score = resume_data.get("overall_resume_score", 0)

    # Ensure score is numeric
    try:
        resume_score = float(resume_score)
    except (TypeError, ValueError):
        resume_score = 0

    video_score = 0
    if video_data and "evaluation" in video_data:
        try:
            video_score = float(video_data["evaluation"].get("communication_score", 0))
        except (TypeError, ValueError):
            video_score = 0

    # Weighted calculation
    if video_score > 0:
        final_score = (resume_score * 0.6) + (video_score * 0.4)
    else:
        final_score = resume_score

    return round(final_score, 2)


# ──────────────────────────────────────────────
# Ranking
# ──────────────────────────────────────────────

def rank_candidates(candidates):
    """Rank all candidates by their final composite score.

    Returns:
        list: Sorted list of candidate dicts with rank field added
    """
    ranked = []

    for candidate_id, data in candidates.items():
        resume = data["resume"]
        video = data["video"]

        final_score = calculate_final_score(resume, video)

        # Video metrics
        video_score = 0
        communication = "N/A"
        transcript_summary = "No video evaluated"

        if video and "evaluation" in video:
            eval_data = video["evaluation"]
            video_score = eval_data.get("communication_score", 0)
            communication = eval_data.get("confidence", "N/A")
            transcript_summary = eval_data.get("summary", "N/A")

        ranked.append({
            "candidate_id": candidate_id,
            "name": resume.get("name", candidate_id),
            "email": resume.get("email", "N/A"),
            "phone": resume.get("phone", "N/A"),
            "education": resume.get("education", "N/A"),
            "experience_years": resume.get("experience_years", 0),
            "skills": resume.get("skills", []),
            "skills_count": len(resume.get("skills", [])),
            "resume_score": resume.get("overall_resume_score", 0),
            "video_score": video_score,
            "final_score": final_score,
            "communication": communication,
            "strengths": ", ".join(resume.get("strengths", [])),
            "weaknesses": ", ".join(resume.get("weaknesses", [])),
            "summary": resume.get("summary", "N/A"),
            "transcript_summary": transcript_summary
        })

    # Sort by final score (highest first)
    ranked = sorted(ranked, key=lambda x: x["final_score"], reverse=True)

    # Assign ranks
    for i, candidate in enumerate(ranked):
        candidate["rank"] = i + 1

    return ranked


# ──────────────────────────────────────────────
# PDF Report Generation
# ──────────────────────────────────────────────

class CandidateReportPDF(FPDF):
    """Custom PDF class for candidate evaluation reports."""

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "AI Candidate Evaluator — Confidential Report", align="R", ln=True)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def generate_pdf_report(ranked_candidates):
    """Generate a professionally formatted PDF evaluation report.

    Args:
        ranked_candidates: List of ranked candidate dicts

    Returns:
        str: Path to the generated PDF file
    """
    os.makedirs("output/reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"output/reports/candidate_report_{timestamp}.pdf"

    pdf = CandidateReportPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Title Page ──
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(41, 128, 185)
    pdf.ln(20)
    pdf.cell(0, 15, "AI Candidate Evaluation", ln=True, align="C")
    pdf.cell(0, 15, "Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True, align="C")
    pdf.cell(0, 8, f"Total Candidates Evaluated: {len(ranked_candidates)}", ln=True, align="C")
    pdf.cell(0, 8, "Scoring: Resume (60%) + Video Interview (40%)", ln=True, align="C")
    pdf.ln(15)

    # ── Summary Table ──
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 10, "Quick Summary", ln=True)
    pdf.ln(3)

    # Table header
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(15, 8, "Rank", fill=True, align="C")
    pdf.cell(55, 8, "Candidate", fill=True, align="C")
    pdf.cell(35, 8, "Final Score", fill=True, align="C")
    pdf.cell(35, 8, "Resume", fill=True, align="C")
    pdf.cell(35, 8, "Video", fill=True, align="C")
    pdf.ln()

    # Table rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=9)
    for i, c in enumerate(ranked_candidates):
        bg = (245, 248, 255) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.cell(15, 7, f"#{c['rank']}", fill=True, align="C")
        pdf.cell(55, 7, str(c['name'])[:30], fill=True)
        pdf.cell(35, 7, f"{c['final_score']}/100", fill=True, align="C")
        pdf.cell(35, 7, f"{c['resume_score']}/100", fill=True, align="C")
        pdf.cell(35, 7, f"{c['video_score']}/100", fill=True, align="C")
        pdf.ln()

    pdf.ln(5)

    # ── Detailed Candidate Sections ──
    for candidate in ranked_candidates:
        pdf.add_page()

        # Candidate header
        pdf.set_fill_color(41, 128, 185)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, f"  #{candidate['rank']}  {candidate['name']}", fill=True, ln=True)
        pdf.ln(5)

        # Score boxes
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)

        # Final score (green)
        pdf.set_fill_color(39, 174, 96)
        pdf.cell(58, 10, f"Final: {candidate['final_score']}/100", fill=True, align="C")
        pdf.cell(3, 10, "")
        # Resume score (blue)
        pdf.set_fill_color(52, 152, 219)
        pdf.cell(58, 10, f"Resume: {candidate['resume_score']}/100", fill=True, align="C")
        pdf.cell(3, 10, "")
        # Video score (purple)
        pdf.set_fill_color(155, 89, 182)
        pdf.cell(58, 10, f"Video: {candidate['video_score']}/100", fill=True, align="C")
        pdf.ln(15)

        pdf.set_text_color(0, 0, 0)

        # Contact info
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "Contact Information", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 6, f"Email: {candidate['email']}     |     Phone: {candidate.get('phone', 'N/A')}", ln=True)
        pdf.cell(0, 6, f"Education: {candidate['education']}     |     Experience: {candidate['experience_years']} years", ln=True)
        pdf.ln(3)

        # Skills
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, f"Skills ({candidate['skills_count']})", ln=True)
        pdf.set_font("Helvetica", size=10)
        skills_text = ", ".join(candidate.get("skills", []))
        pdf.multi_cell(0, 6, skills_text if skills_text else "N/A")
        pdf.ln(3)

        # Strengths
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(39, 174, 96)
        pdf.cell(0, 7, "Strengths", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 6, candidate["strengths"] if candidate["strengths"] else "N/A")
        pdf.ln(3)

        # Weaknesses
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(231, 76, 60)
        pdf.cell(0, 7, "Areas for Improvement", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 6, candidate.get("weaknesses", "N/A") if candidate.get("weaknesses") else "N/A")
        pdf.ln(3)

        # Communication
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "Communication Assessment", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 6, f"Confidence Level: {candidate['communication']}", ln=True)
        pdf.multi_cell(0, 6, f"Video Summary: {candidate['transcript_summary']}")
        pdf.ln(3)

        # Overall summary
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(41, 128, 185)
        pdf.cell(0, 7, "Overall Summary", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 6, candidate["summary"])

        # Divider
        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.output(report_path)
    print(f"📄 Report saved to {report_path}")
    return report_path


# ──────────────────────────────────────────────
# CLI Entry Point
# ──────────────────────────────────────────────

def run_ranking():
    """Run the complete ranking pipeline from CLI."""
    print("=== Phase 3 — Candidate Ranking ===")
    candidates = load_all_candidates()

    if not candidates:
        print("❌ No candidates found in output folder!")
        return

    ranked = rank_candidates(candidates)

    print("\n🏆 === FINAL RANKINGS ===")
    for c in ranked:
        print(f"  #{c['rank']} | {c['name']} | Final Score: {c['final_score']}/100")

    report_path = generate_pdf_report(ranked)
    print(f"\n✅ Done! Report at: {report_path}")


if __name__ == "__main__":
    run_ranking()
