AI Video Insight Template

Overview

This is a Streamlit-based Python application designed to process a public video URL (e.g., YouTube, Loom) and extract key communication insights using Google's Gemini API for multimodal transcription and analysis.

The tool focuses on demonstrating robust backend development, modularity, and the practical integration of third-party APIs, fulfilling the Python Assessment requirements.

Technical Choices

Component

Tool / Library

Reason for Selection

Video/Audio Extraction

yt-dlp (via Python API)

Industry-standard, highly reliable, and now used via its native API for robust control and error handling.

System Dependency

FFmpeg / ffprobe

MANDATORY: Required by yt-dlp for format conversion. The code now actively checks for these binaries before attempting extraction to provide clear error feedback.

Transcription & Analysis

Google Gemini API (gemini-2.5-flash)

Multimodal capability allows for sending the audio file directly to the model for transcription and analysis, simplifying the workflow and enforcing structured JSON output (Pydantic).

Structure & Resilience

Modular core/ package & Exponential Backoff

Ensures separation of concerns and guarantees the application retries API calls gracefully upon encountering transient server overload errors (503/429).

Setup and Installation

0. Install System Prerequisites (FFmpeg / ffprobe)

This tool relies on external binaries for media processing. The code will fail immediately if these are not available.

Windows (via Chocolatey): choco install ffmpeg

macOS (via Homebrew): brew install ffmpeg

Linux (or Streamlit Cloud Environment): Requires ffmpeg and nodejs. This is handled automatically by the deployment configuration file (apt.txt).

1. Clone the repository

git clone <repository-link>
cd AI-Video-Analyzer-Template


2. Create and Activate Virtual Environment

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`


3. Install Python Dependencies

pip install -r requirements.txt


4. Configure API Key

Create a file named .env in the root directory and add your key:

GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
