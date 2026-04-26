"""
Phase 1 — Resume Parser
Extracts text from PDF resumes and uses Groq LLaMA for AI-powered analysis.
Returns structured candidate data with scores.
"""

import pdfplumber
from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_text_from_pdf(pdf_path):
    """Extract all text content from a PDF file using pdfplumber."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise RuntimeError(f"Error reading PDF: {e}")

    return text.strip()


def analyze_resume(text):
    """Send resume text to Groq LLaMA for AI-powered analysis.

    Returns a structured JSON with candidate details, skills, scores, etc.
    """
    prompt = f"""
You are an expert HR recruiter. Analyze the following resume and return a JSON object with exactly these fields:

{{
  "name": "candidate full name",
  "email": "email address or null",
  "phone": "phone number or null",
  "skills": ["list", "of", "skills"],
  "experience_years": 0,
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "education": "highest education qualification",
  "overall_resume_score": 0,
  "summary": "2-3 line summary of this candidate"
}}

Score the resume out of 100 based on clarity, skills, and experience.
Return only the JSON, no extra text.

Resume:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        raw = response.choices[0].message.content.strip()
        # Clean markdown code fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)

        # Validate required fields
        required_fields = ["name", "skills", "overall_resume_score", "summary"]
        for field in required_fields:
            if field not in result:
                result[field] = "N/A" if field != "skills" else []

        return result

    except json.JSONDecodeError as e:
        print(f"Error parsing AI response: {e}")
        return None
    except Exception as e:
        print(f"Error during resume analysis: {e}")
        return None


def save_candidate(result, candidate_id):
    """Save candidate resume analysis to a JSON file."""
    os.makedirs("output", exist_ok=True)
    path = f"output/{candidate_id}_resume.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Resume analysis saved to {path}")
    return path


def parse_resume(pdf_path, candidate_id=None):
    """Main function: parse a resume PDF and return structured analysis.

    Args:
        pdf_path: Path to the PDF resume file
        candidate_id: Optional candidate identifier (auto-generated from name if not provided)

    Returns:
        dict: Structured candidate analysis data, or None on failure
    """
    print(f"📄 Parsing resume: {pdf_path}")

    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("❌ Could not extract text from PDF")
        return None

    print(f"📝 Extracted {len(text)} characters from PDF")

    # AI analysis
    result = analyze_resume(text)
    if not result:
        print("❌ AI analysis failed")
        return None

    # Determine candidate ID
    if not candidate_id:
        candidate_id = result.get("name", "candidate").replace(" ", "_")

    # Save result
    save_candidate(result, candidate_id)
    print(f"✅ Resume analysis complete for: {result.get('name', candidate_id)}")

    return result


if __name__ == "__main__":
    parse_resume("data/resumes/sample.pdf")
