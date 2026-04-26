"""
Phase 2 — Video Interview Evaluator
Extracts audio from video, transcribes with Whisper, and evaluates communication
skills using Groq LLaMA AI.
"""

from groq import Groq
import json
import os
import subprocess
import shutil
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def check_ffmpeg():
    """Check if FFmpeg is available on the system."""
    if shutil.which("ffmpeg") is None:
        raise EnvironmentError(
            "FFmpeg is not installed or not in PATH.\n"
            "Install it:\n"
            "  Windows: choco install ffmpeg\n"
            "  macOS:   brew install ffmpeg\n"
            "  Linux:   sudo apt install ffmpeg"
        )


def extract_audio(video_path, audio_output="temp_audio.wav"):
    """Extract audio from video file using FFmpeg.

    Args:
        video_path: Path to the video file
        audio_output: Path for the output WAV file

    Returns:
        str: Path to the extracted audio file
    """
    check_ffmpeg()

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    print("Extracting audio from video...")
    command = [
        "ffmpeg", "-i", video_path,
        "-ar", "16000",    # 16kHz sample rate (optimal for Whisper)
        "-ac", "1",        # Mono channel
        "-y", audio_output  # Overwrite output
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if result.returncode != 0:
        raise RuntimeError("FFmpeg failed to extract audio from video")

    print(f"Audio extracted to {audio_output}")
    return audio_output


def transcribe_audio(audio_path):
    """Transcribe audio to text using OpenAI Whisper.

    Args:
        audio_path: Path to the audio WAV file

    Returns:
        str: Transcribed text
    """
    print("Transcribing audio with Whisper...")
    import whisper

    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcript = result["text"].strip()
        print(f"Transcript length: {len(transcript)} characters")
        return transcript
    except Exception as e:
        print(f"Whisper transcription error: {e}")
        return ""


def analyze_transcript(transcript):
    """Send transcript to Groq LLaMA for communication analysis.

    Args:
        transcript: The transcribed interview text

    Returns:
        dict: Structured evaluation with scores
    """
    if not transcript:
        return {
            "communication_score": 0,
            "confidence": "Unable to evaluate",
            "clarity": "Unable to evaluate",
            "key_points": [],
            "strengths": [],
            "improvements": [],
            "summary": "No speech detected in video"
        }

    prompt = f"""
You are an expert HR interviewer. Analyze the following interview transcript and return a JSON object with exactly these fields:

{{
  "communication_score": 0,
  "confidence": "High/Medium/Low",
  "clarity": "High/Medium/Low",
  "key_points": ["point 1", "point 2", "point 3"],
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"],
  "summary": "2-3 line summary of candidate's communication"
}}

Score communication out of 100 based on clarity, confidence, and content.
Return only the JSON, no extra text.

Transcript:
{transcript}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)

    except json.JSONDecodeError as e:
        print(f"Error parsing AI response: {e}")
        return {
            "communication_score": 0,
            "confidence": "Error",
            "clarity": "Error",
            "key_points": [],
            "strengths": [],
            "improvements": [],
            "summary": "Error during AI analysis"
        }
    except Exception as e:
        print(f"Error during transcript analysis: {e}")
        return None


def save_video_result(result, transcript, candidate_id):
    """Save video evaluation results to a JSON file."""
    os.makedirs("output", exist_ok=True)
    full_result = {
        "candidate_id": candidate_id,
        "transcript": transcript,
        "evaluation": result
    }
    path = f"output/{candidate_id}_video.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(full_result, f, indent=2, ensure_ascii=False)
    print(f"Video evaluation saved to {path}")
    return full_result


def evaluate_video(video_path, candidate_id="candidate"):
    """Main function: evaluate a video interview.

    Pipeline: Video → Audio extraction → Whisper transcription → AI analysis

    Args:
        video_path: Path to the video file
        candidate_id: Candidate identifier for file naming

    Returns:
        dict: Complete evaluation with transcript and scores
    """
    print(f"Evaluating video: {video_path}")

    # Step 1 — Extract audio
    audio_path = extract_audio(video_path)

    # Step 2 — Transcribe with Whisper
    transcript = transcribe_audio(audio_path)

    # Step 3 — AI analysis
    result = analyze_transcript(transcript)

    # Step 4 — Save results
    full_result = save_video_result(result, transcript, candidate_id)

    # Cleanup temporary audio file
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print("Temporary audio file cleaned up")

    print(f"Video evaluation complete for: {candidate_id}")
    return full_result


if __name__ == "__main__":
    evaluate_video("data/videos/sample.mp4", candidate_id="Jay_Patel")
