# 🤖 AI Candidate Evaluator

An AI-powered candidate evaluation system that automates the hiring pipeline using resume analysis, video interview evaluation, and intelligent ranking.

---

## 📌 Overview

This project uses **Groq's LLaMA 3.3 70B** for intelligent analysis and **OpenAI Whisper** for speech-to-text transcription. It provides a complete Streamlit-based web interface for HR teams to:

1. **Upload & analyze resumes** (PDF) — extracts skills, experience, education, and provides an AI-generated score
2. **Upload & evaluate video interviews** — transcribes speech via Whisper, then evaluates communication skills with AI
3. **Rank all candidates** — combines resume + video scores with configurable weights
4. **Generate PDF reports** — professional evaluation reports ready for download

---

## 🏗️ Architecture

```
ai_candidate_evaluator/
├── main.py                      # Streamlit web application (entry point)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
│
├── phase1_resume/               # Phase 1 — Resume Parsing
│   ├── __init__.py
│   └── resume_parser.py         # PDF extraction + AI analysis
│
├── phase2_video/                # Phase 2 — Video Evaluation
│   ├── __init__.py
│   └── video_evaluator.py       # Audio extraction + Whisper + AI analysis
│
├── phase3_ranking/              # Phase 3 — Ranking & Reports
│   ├── __init__.py
│   └── ranker.py                # Score calculation, ranking, PDF generation
│
├── utils/                       # Shared utilities
│   ├── __init__.py
│   └── helpers.py               # Common helper functions
│
├── data/                        # Input data (git-ignored)
│   ├── resumes/                 # Uploaded resume PDFs
│   └── videos/                  # Uploaded interview videos
│
└── output/                      # Generated output (git-ignored)
    ├── *.json                   # Individual candidate evaluation JSONs
    └── reports/                 # Generated PDF reports
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **FFmpeg** (required for video processing)
  - Windows: `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **Groq API Key** — Get one free at [console.groq.com](https://console.groq.com/)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jaypateljp02/ai-candidate-evaluator.git
   cd ai-candidate-evaluator
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Groq API key
   ```

5. **Run the application**
   ```bash
   streamlit run main.py
   ```

---

## 🔧 How It Works

### Phase 1 — Resume Analysis
- Extracts text from PDF resumes using `pdfplumber`
- Sends text to Groq LLaMA 3.3 for intelligent analysis
- Returns: name, email, skills, experience, education, strengths, weaknesses, and an overall score (0–100)

### Phase 2 — Video Interview Evaluation
- Extracts audio from uploaded video using `FFmpeg`
- Transcribes speech using OpenAI's `Whisper` model
- Sends transcript to Groq LLaMA 3.3 for communication analysis
- Returns: communication score (0–100), confidence level, clarity, key points, and summary

### Phase 3 — Ranking & Reporting
- Loads all evaluated candidates from JSON output files
- Calculates final score: **60% resume + 40% video** (if video exists)
- Ranks candidates by final score
- Generates a professionally formatted PDF report

---

## 📊 Scoring System

| Component        | Weight | Source                    |
|------------------|--------|---------------------------|
| Resume Score     | 60%    | AI analysis of resume PDF |
| Video Score      | 40%    | AI analysis of interview  |
| **Final Score**  | 100%   | Weighted combination      |

> If no video is uploaded, the final score equals the resume score.

---

## 🛠️ Tech Stack

| Technology     | Purpose                          |
|----------------|----------------------------------|
| Python 3.9+    | Core language                    |
| Streamlit      | Web UI framework                 |
| Groq (LLaMA)   | AI-powered analysis              |
| OpenAI Whisper | Speech-to-text transcription     |
| pdfplumber     | PDF text extraction              |
| FFmpeg         | Audio extraction from video      |
| fpdf2          | PDF report generation            |
| pandas         | Data manipulation                |
| scikit-learn   | ML utilities                     |
| python-dotenv  | Environment variable management  |

---

## 📸 Screenshots

### Home Page
The landing page provides an overview of all three evaluation phases.

### Candidate Evaluation
Upload a resume PDF and optionally a video interview for AI-powered analysis.

### Rankings Dashboard
View all evaluated candidates ranked by their composite score.

### PDF Report
Download a professionally formatted evaluation report.

---

## 📝 Environment Variables

| Variable       | Description          | Required |
|----------------|----------------------|----------|
| `GROQ_API_KEY` | Your Groq API key    | ✅ Yes   |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Jay Patel**
- GitHub: [@jaypateljp02](https://github.com/jaypateljp02)

---

*Built with ❤️ using Python, Groq AI, and Streamlit*
