Video Insight Analyzer - Python Assessment (November 2025)

Overview

This is a Streamlit-based Python application designed to process a public video URL (e.g., YouTube, Loom) and extract key communication insights using Google's Gemini API for multimodal transcription and analysis.

The tool focuses on demonstrating robust backend development, modularity, and the practical integration of third-party APIs.

Technical Choices

Component

Tool / Library

Reason for Selection

Video/Audio Extraction

yt-dlp

Industry-standard, highly reliable, and supports a vast range of public video sources (YouTube, etc.).

Transcription & Analysis

Google Gemini API (gemini-2.5-flash)

Multimodal capability allows for sending the audio file directly to the model for transcription and simultaneous analysis, simplifying the workflow and maintaining a single API dependency. The use of a JSON schema ensures reliable, structured output.

Web Interface

streamlit

Provides a functional, deployable UI with minimal code, adhering to the requirement to keep the UI "extremely simple."

Structure & Secrets

Modular core/ package and .env

Enforces separation of concerns, ensures Python proficiency, and follows security best practices by keeping the API key out of the source code.

Setup and Installation

0. Install Prerequisites: ffmpeg and ffprobe (MANDATORY)

The yt-dlp library requires the external FFmpeg suite to extract and convert audio files. You must install this system utility and ensure it is accessible in your system's PATH.

Windows (via Chocolatey or manually):

# If using Chocolatey package manager:
choco install ffmpeg


Alternatively, download the binaries from ffmpeg.org and add the /bin directory to your system's PATH.

macOS (via Homebrew):

brew install ffmpeg


Linux (Debian/Ubuntu):

sudo apt update
sudo apt install ffmpeg


1. Clone the repository (or set up the directory)

git clone <repository-link>
cd VideoInsightAnalyzer


2. Create and Activate Virtual Environment

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`


3. Install Dependencies

pip install -r requirements.txt


4. Configure API Key

Create a file named .env in the root directory and add your key:

GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE


How to Run the Application

Ensure your virtual environment is active.

Run the Streamlit app from the root directory:

streamlit run app.py


The application will open in your browser, ready to accept a video URL.