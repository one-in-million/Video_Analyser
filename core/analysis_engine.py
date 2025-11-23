import os
import tempfile
import json
import subprocess
import time
import shutil # Required for cleaning up temporary directory
from contextlib import contextmanager
from typing import List, Any

# Third-party libraries
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import yt_dlp.utils # For handling yt-dlp specific exceptions
import yt_dlp

# --- Pydantic Schema for Structured Output (MANDATORY ASSESSMENT METRICS) ---
class CommunicationAnalysis(BaseModel):
    """Defines the structured output for the communication analysis."""
    clarity_score: int = Field(..., ge=0, le=100, description="A numerical score (0-100) indicating the speaker's fluency, coherence, and grammar, and pace.")
    communication_focus: str = Field(..., description="A single, concise sentence summarizing the main topic of the video.")
    transcript: str = Field(..., description="The complete text transcription of the audio content.")


# --- 1. Audio Extraction Utility (USING YT-DLP API) ---

@contextmanager
def extract_audio_from_url(video_url: str):
    """
    Uses the yt-dlp Python API to extract MP3 audio from a video URL.
    Performs binary checks and intelligent error handling.

    Yields:
        str: Path to extracted MP3 file.
    """

    # 1. Verify ffmpeg & ffprobe (Crucial for Streamlit Cloud deployment check)
    def check_binary(bin_name):
        try:
            # Check for binary in PATH
            subprocess.run([bin_name, "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    if not check_binary("ffmpeg") or not check_binary("ffprobe"):
        # This will be caught by the outer try/except and result in an error message
        raise RuntimeError("ffmpeg and/or ffprobe not installed. This is the root cause of the error on Streamlit Cloud.")
    
    # 2. Setup environment and options
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "audio.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "noplaylist": True,
        "quiet": True,
        "verbose": False,
        "no_check_certificate": True, # For server security/firewall issues
        "extractor_args": "youtube:player_client=web", # Explicitly use web client for decryption
        
        # Post-processor to convert to MP3 using ffmpeg
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }
        ]
    }

    # 3. Attempt extraction
    try:
        print("[INFO] Starting audio extraction via yt-dlp API...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Verify output file exists
        if not os.path.exists(output_path):
            raise RuntimeError(
                "yt-dlp download completed but failed to create the final MP3 file. Check post-processing logs."
            )

        print(f"[INFO] Audio extracted to: {output_path}")
        yield output_path

    except yt_dlp.utils.DownloadError as e:
        # Smart error detection for clean display to the user/assessor
        msg = str(e).lower()
        if "sign in" in msg or "confirm you're not a bot" in msg:
            raise RuntimeError(
                "Video requires login or is age-restricted. Please use a public URL."
            )
        raise RuntimeError(f"yt-dlp failed to extract audio: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error during extraction: {str(e)}")

    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

            
# --- 2. Multimodal Analysis (Gemini) ---

def analyze_audio_file(
    audio_path: str, 
    client: genai.Client,
    max_retries: int = 8
) -> CommunicationAnalysis:
    """
    Uploads the audio file to Gemini, requests transcription and analysis,
    and returns the structured results, implementing exponential backoff.
    """
    print(f"[INFO] Starting Gemini analysis for: {audio_path}")
    uploaded_file = None
    
    try:
        # 1. Upload the audio file using the Files API
        uploaded_file = client.files.upload(file=audio_path)
        print(f"[INFO] Uploaded to Gemini: {uploaded_file.name} ({uploaded_file.mime_type})")

        # 2. Define the LLM instructions and structured output format
        system_instruction = (
            "You are a Senior Communication Analyst. Your primary task is to accurately transcribe "
            "the provided audio file and generate the **Clarity Score (0-100)** and a **Communication Focus** "
            "sentence. You MUST strictly follow the provided JSON schema for the output. "
            "The Clarity Score reflects fluency, coherence, and grammar."
        )

        prompt = (
            "Analyze the audio. Generate the full, accurate transcript, calculate the Clarity Score (0-100), "
            "and state the Communication Focus (a single, concise sentence summarizing the main topic)."
        )

        # 3. Call the model with structured output, implementing retries
        for attempt in range(max_retries):
            try:
                print(f"[INFO] Attempt {attempt + 1}/{max_retries} to call Gemini model...")
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt, uploaded_file],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        response_schema=CommunicationAnalysis, # Enforce Pydantic schema
                        temperature=0.0,
                    )
                )

                # 4. Parse the structured JSON response
                json_string = response.text
                analysis_data = json.loads(json_string)
                
                # Validation and return
                return CommunicationAnalysis.model_validate(analysis_data)
            
            except genai.errors.APIError as e:
                # Check for transient errors (500, 503, 429)
                if e.response.status_code in (500, 503, 429) and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"[WARNING] Transient error ({e.response.status_code}) encountered. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Reraise the exception if it's a permanent error or max retries reached
                    error_detail = json.loads(e.response.text).get('error', {}).get('message', 'No specific message provided.')
                    raise ConnectionError(f"Gemini API call failed after {attempt + 1} attempts. Detail: {e.response.status_code} - {error_detail}") from e

        # If loop completes without returning
        raise ConnectionError(f"Gemini API call failed after {max_retries} attempts due to model overload/unavailability.")

    except Exception as e:
        # Catch all other errors (e.g., File API errors, JSON parsing errors)
        print(f"[ERROR] An unexpected error occurred during analysis: {e}")
        raise
    finally:
        # 5. Clean up the uploaded file from the Gemini service
        if uploaded_file:
            print(f"[INFO] Deleting uploaded file: {uploaded_file.name}")
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception as delete_e:
                print(f"[WARNING] Failed to delete uploaded file {uploaded_file.name}. Error: {delete_e}")
            

# --- 3. Main Orchestration Function ---

def process_video_insights(video_url: str, client: genai.Client) -> CommunicationAnalysis:
    """
    Orchestrates the entire process: extract audio, analyze, and return results.
    """
    
    # Context manager handles temporary audio file creation and cleanup automatically
    try:
        with extract_audio_from_url(video_url) as audio_path:
            # Pass the path to the analysis function
            analysis_result = analyze_audio_file(audio_path, client)
            return analysis_result
    
    except RuntimeError as e:
        # Catch expected operational errors (ffmpeg missing, bad URL)
        raise ValueError(f"Video Processing Error: {e}")
    
    except ConnectionError as e:
        # Catch API communication errors (Gemini upload/call failure)
        raise ConnectionError(f"API Error: {e}")
    
    except Exception as e:
        # Catch all other unexpected errors
        raise Exception(f"An unexpected critical error occurred: {str(e)}")