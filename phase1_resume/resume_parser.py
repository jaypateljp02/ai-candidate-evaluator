import pdfplumber
from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def analyze_resume(text):
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
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def save_candidate(result, candidate_id):
    os.makedirs("output", exist_ok=True)
    path = f"output/{candidate_id}_resume.json"
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved to {path}")

def parse_resume(pdf_path, candidate_id=None):
    print(f"Parsing: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("Could not extract text from PDF")
        return None
    result = analyze_resume(text)
    if not candidate_id:
        candidate_id = result.get("name", "candidate").replace(" ", "_")
    save_candidate(result, candidate_id)
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    parse_resume("data/resumes/sample.pdf")
