import whisper
from groq import Groq
import json
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_audio(video_path, audio_output="temp_audio.wav"):
    print("Extracting audio from video...")
    command = [
        "ffmpeg", "-i", video_path,
        "-ar", "16000",
        "-ac", "1",
        "-y", audio_output
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Audio extracted to {audio_output}")
    return audio_output

def transcribe_audio(audio_path):
    print("Transcribing audio with Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcript = result["text"].strip()
    print(f"Transcript: {transcript}")
    return transcript

def analyze_transcript(transcript):
    if not transcript:
        return {
            "communication_score": 0,
            "confidence": "Unable to evaluate",
            "clarity": "Unable to evaluate",
            "key_points": [],
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
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def save_video_result(result, transcript, candidate_id):
    os.makedirs("output", exist_ok=True)
    full_result = {
        "candidate_id": candidate_id,
        "transcript": transcript,
        "evaluation": result
    }
    path = f"output/{candidate_id}_video.json"
    with open(path, "w") as f:
        json.dump(full_result, f, indent=2)
    print(f"Saved to {path}")
    return full_result

def evaluate_video(video_path, candidate_id="candidate"):
    print(f"Evaluating video: {video_path}")

    # Step 1 - Extract audio
    audio_path = extract_audio(video_path)

    # Step 2 - Transcribe
    transcript = transcribe_audio(audio_path)

    # Step 3 - Analyze
    result = analyze_transcript(transcript)

    # Step 4 - Save
    full_result = save_video_result(result, transcript, candidate_id)

    # Cleanup temp audio
    if os.path.exists(audio_path):
        os.remove(audio_path)

    print(json.dumps(full_result, indent=2))
    return full_result

if __name__ == "__main__":
    evaluate_video("data/videos/sample.mp4", candidate_id="Jay_Patel")
