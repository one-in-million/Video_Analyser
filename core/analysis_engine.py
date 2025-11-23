import os
import tempfile
import json
import subprocess
from contextlib import contextmanager

# Third-party libraries
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# --- Pydantic Schema for Structured Output (ENSURES RELIABILITY) ---
# This class defines the exact JSON structure the LLM MUST return.
class CommunicationAnalysis(BaseModel):
    """Defines the structured output for the communication analysis."""
    clarity_score: int = Field(..., ge=0, le=100, description="A numerical score (0-100) indicating the speaker's fluency, grammar, and pace.")
    communication_focus: str = Field(..., description="A single, concise sentence summarizing the main topic of the video.")
    transcript: str = Field(..., description="The complete text transcription of the audio content.")


# --- 1. Audio Extraction Utility ---

@contextmanager
def extract_audio_from_url(video_url: str):
    """
    Uses yt-dlp to extract the audio from a video URL and saves it to a
    temporary MP3 file. The file is automatically cleaned up on exit.

    Args:
        video_url (str): The public URL of the video (YouTube, Loom, etc.).

    Yields:
        str: The path to the temporary MP3 file.
    """
    # Create a temporary file path
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, "audio.mp3")

    # yt-dlp command to extract audio and convert to mp3
    # Note: This requires the external 'ffmpeg' and 'ffprobe' utilities to be installed.
    command = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "mp3",
        "--output", temp_file_path,
        video_url
    ]

    try:
        # Run the command
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        if not os.path.exists(temp_file_path):
             raise FileNotFoundError(f"yt-dlp ran successfully but failed to create the expected file at {temp_file_path}.")

        yield temp_file_path

    except subprocess.CalledProcessError as e:
        error_message = f"Audio extraction failed. Please ensure 'ffmpeg' and 'ffprobe' are installed and in your system PATH. Detail: {e.stderr}"
        print(f"Subprocess error: {error_message}")
        raise ValueError(f"Could not extract audio from URL. Check if the URL is valid and public. Detail: {error_message.strip()}") from e
    except Exception as e:
        print(f"An unexpected error occurred during audio extraction: {e}")
        raise
    finally:
        # Cleanup the temporary directory and its contents
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            
# --- 2. Multimodal Analysis (Gemini) ---

def analyze_audio_file(
    audio_path: str, 
    client: genai.Client
) -> CommunicationAnalysis:
    """
    Uploads the audio file to Gemini, requests transcription and analysis,
    and returns the structured results.

    Args:
        audio_path (str): Path to the local audio file.
        client (genai.Client): Initialized Gemini client instance.

    Returns:
        CommunicationAnalysis: The Pydantic object containing the score and focus.
    """
    print(f"Starting Gemini analysis for: {audio_path}")
    uploaded_file = None
    try:
        # 1. Upload the audio file using the Files API
        # This is necessary for larger files, but good practice regardless.
        uploaded_file = client.files.upload(file=audio_path)
        print(f"File uploaded to Gemini: {uploaded_file.name} ({uploaded_file.mime_type})")

        # 2. Define the LLM instructions and structured output format
        system_instruction = (
            "You are a Senior Communication Analyst. Your task is to transcribe "
            "the provided audio file and generate a professional communication analysis. "
            "You MUST strictly follow the provided JSON schema for the output. "
            "The Clarity Score should reflect the speaker's fluency, coherence, and grammar, "
            "and the Communication Focus must be a single, concise, professional sentence."
        )

        prompt = "Analyze the provided audio. Generate the full, accurate transcript, calculate the Clarity Score (0-100), and state the Communication Focus."

        # 3. Call the model with structured output
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, uploaded_file],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=CommunicationAnalysis,
                temperature=0.0,
            )
        )

        # 4. Parse the structured JSON response
        # The response text will be a JSON string conforming to the Pydantic model
        json_string = response.text
        
        # 5. Validate and return the Pydantic object
        analysis_data = json.loads(json_string)
        return CommunicationAnalysis.model_validate(analysis_data)

    except genai.errors.APIError as e:
        print(f"Gemini API Error: {e}")
        raise ConnectionError(f"Gemini API call failed. Check your API Key and usage limits. Detail: {e}") from e
    except Exception as e:
        print(f"An unexpected error occurred during analysis: {e}")
        raise
    finally:
        # 5. Clean up the uploaded file from the Gemini service
        if uploaded_file:
            print(f"Deleting uploaded file: {uploaded_file.name}")
            client.files.delete(name=uploaded_file.name)
            

# --- 3. Main Orchestration Function ---

def process_video_insights(video_url: str, client: genai.Client) -> CommunicationAnalysis:
    """
    Orchestrates the entire process: extract audio, analyze, and return results.
    """
    print(f"Starting process for URL: {video_url}")
    
    # Context manager handles temporary file creation and cleanup automatically
    with extract_audio_from_url(video_url) as audio_path:
        print(f"Audio successfully extracted to: {audio_path}")
        
        # Pass the path to the analysis function
        analysis_result = analyze_audio_file(audio_path, client)
        
        return analysis_result