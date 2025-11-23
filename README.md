AI Video Insight Template

Overview

This is a Streamlit-based Python application designed to process a public video URL (e.g., YouTube, Loom) and extract key communication insights using Google's Gemini API for multimodal transcription and analysis.

The tool focuses on demonstrating robust backend development, modularity, and the practical integration of third-party APIs, fulfilling the Python Assessment requirements.

Technical Choices

Component

Tool / Library

Reason for Selection

Video/Audio Extraction

yt-dlp

Industry-standard, highly reliable, and supports a vast range of public video sources.

System Dependency

FFmpeg / youtube-dl

MANDATORY: Required by yt-dlp to convert and process extracted audio streams. Must be installed on the host system (locally or on the server).

Transcription & Analysis

Google Gemini API (gemini-2.5-flash)

Multimodal capability allows for sending the audio file directly to the model for transcription and analysis, simplifying the workflow and enforcing structured JSON output.

Web Interface

streamlit

Provides a functional, deployable UI with minimal code, adhering to the requirement to keep the UI "extremely simple."

Structure & Resilience

Modular backend/ package & Exponential Backoff

Ensures separation of concerns and guarantees the application retries API calls gracefully upon encountering server overload errors (503/429).

Setup and Installation

0. Install System Prerequisites (FFmpeg / youtube-dl)

This tool relies on external binaries for media processing. You must install one of the following on your operating system:

Windows (via Chocolatey): choco install ffmpeg

macOS (via Homebrew): brew install ffmpeg

Linux (or Streamlit Cloud Environment): Requires the ffmpeg or youtube-dl system package. This is handled automatically by the deployment configuration file (packages.txt).

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
