import json
import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

def load_all_candidates(output_dir="output"):
    candidates = {}

    for file in os.listdir(output_dir):
        if file.endswith("_resume.json"):
            candidate_id = file.replace("_resume.json", "")
            resume_path = os.path.join(output_dir, file)
            video_path = os.path.join(output_dir, f"{candidate_id}_video.json")

            with open(resume_path) as f:
                resume_data = json.load(f)

            video_data = None
            if os.path.exists(video_path):
                with open(video_path) as f:
                    video_data = json.load(f)

            candidates[candidate_id] = {
                "resume": resume_data,
                "video": video_data
            }

    print(f"Loaded {len(candidates)} candidate(s)")
    return candidates

def calculate_final_score(resume_data, video_data):
    resume_score = resume_data.get("overall_resume_score", 0)

    video_score = 0
    if video_data and "evaluation" in video_data:
        video_score = video_data["evaluation"].get("communication_score", 0)

    # Weighted score — resume 60%, video 40%
    if video_score > 0:
        final_score = (resume_score * 0.6) + (video_score * 0.4)
    else:
        final_score = resume_score

    return round(final_score, 2)

def rank_candidates(candidates):
    ranked = []

    for candidate_id, data in candidates.items():
        resume = data["resume"]
        video = data["video"]

        final_score = calculate_final_score(resume, video)

        video_score = 0
        communication = "N/A"
        transcript_summary = "No video evaluated"

        if video and "evaluation" in video:
            video_score = video["evaluation"].get("communication_score", 0)
            communication = video["evaluation"].get("confidence", "N/A")
            transcript_summary = video["evaluation"].get("summary", "N/A")

        ranked.append({
            "candidate_id": candidate_id,
            "name": resume.get("name", candidate_id),
            "email": resume.get("email", "N/A"),
            "education": resume.get("education", "N/A"),
            "experience_years": resume.get("experience_years", 0),
            "skills_count": len(resume.get("skills", [])),
            "resume_score": resume.get("overall_resume_score", 0),
            "video_score": video_score,
            "final_score": final_score,
            "communication": communication,
            "strengths": ", ".join(resume.get("strengths", [])),
            "summary": resume.get("summary", "N/A"),
            "transcript_summary": transcript_summary
        })

    ranked = sorted(ranked, key=lambda x: x["final_score"], reverse=True)

    for i, candidate in enumerate(ranked):
        candidate["rank"] = i + 1

    return ranked

def generate_pdf_report(ranked_candidates):
    os.makedirs("output/reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"output/reports/candidate_report_{timestamp}.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "AI Candidate Evaluation Report", fill=True, ln=True, align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True, align="C")
    pdf.cell(0, 8, f"Total Candidates Evaluated: {len(ranked_candidates)}", ln=True, align="C")
    pdf.ln(5)

    for candidate in ranked_candidates:
        # Candidate header
        pdf.set_fill_color(230, 240, 255)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, f"Rank #{candidate['rank']} - {candidate['name']}", fill=True, ln=True)
        pdf.ln(2)

        # Scores row
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(41, 128, 185)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(63, 8, f"Final Score: {candidate['final_score']}/100", fill=True, align="C")
        pdf.cell(63, 8, f"Resume Score: {candidate['resume_score']}/100", fill=True, align="C")
        pdf.cell(63, 8, f"Video Score: {candidate['video_score']}/100", fill=True, align="C")
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)

        # Details
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 7, f"Email: {candidate['email']}    |    Experience: {candidate['experience_years']} years    |    Skills: {candidate['skills_count']}", ln=True)
        pdf.cell(0, 7, f"Education: {candidate['education']}", ln=True)
        pdf.cell(0, 7, f"Communication: {candidate['communication']}", ln=True)
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "Strengths:", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 6, candidate["strengths"])
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "Summary:", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 6, candidate["summary"])
        pdf.ln(5)

        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    pdf.output(report_path)
    print(f"Report saved to {report_path}")
    return report_path

def run_ranking():
    print("=== Phase 3 - Candidate Ranking ===")
    candidates = load_all_candidates()

    if not candidates:
        print("No candidates found in output folder!")
        return

    ranked = rank_candidates(candidates)

    print("\n=== FINAL RANKINGS ===")
    for c in ranked:
        print(f"Rank #{c['rank']} | {c['name']} | Final Score: {c['final_score']}/100")

    report_path = generate_pdf_report(ranked)
    print(f"\nDone! Report at: {report_path}")

if __name__ == "__main__":
    run_ranking()
