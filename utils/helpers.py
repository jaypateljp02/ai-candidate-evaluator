# Utility Helpers
# Common helper functions used across all phases.

import os
import json
from dotenv import load_dotenv


def load_env():
    """Load environment variables from .env file."""
    load_dotenv()
    return os.getenv("GROQ_API_KEY")


def ensure_directories():
    """Create required directories if they don't exist."""
    dirs = [
        "data/resumes",
        "data/videos",
        "output",
        "output/reports"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def safe_json_parse(raw_text):
    """Safely parse JSON from AI response, stripping markdown code fences."""
    cleaned = raw_text.strip()
    # Remove markdown code fences
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    return json.loads(cleaned)


def save_json(data, filepath):
    """Save data as JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def load_json(filepath):
    """Load JSON data from file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
