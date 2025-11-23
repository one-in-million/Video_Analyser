# 🎥 AI-Powered Video Communication Analyzer (Streamlit)

## Overview

This is a robust Streamlit-based Python application designed to process a public video URL (e.g., YouTube, Loom) and extract key communication insights using Google's Gemini API for multimodal transcription and analysis.

The tool demonstrates robust backend development, modularity, and the practical integration of third-party APIs by delivering a full transcript, calculating a numerical clarity score (0-100), and identifying the core communication focus as a concise summary.

---

## Technical Choices

| Component | Tool / Library | Reason for Selection |
| :--- | :--- | :--- |
| **Video/Audio Extraction** | `yt-dlp` (via `subprocess`) | Industry-standard, highly reliable tool used for direct audio stream extraction from various public video platforms. |
| **System Dependency (MANDATORY)** | `FFmpeg` / `ffprobe` | **Required** by `yt-dlp` for format conversion and reliable audio extraction. The application actively requires these binaries to be present in the system PATH. |
| **Transcription & Analysis** | Google Gemini API (`gemini-2.5-flash`) | Multimodal capability allows for sending the audio file directly to the model for transcription and analysis, simplifying the workflow and enforcing structured JSON output (`Pydantic`). |
| **Structured Output** | `Pydantic` | Enforces a strict, reliable JSON schema for the output, ensuring the Streamlit application receives consistent data (e.g., `clarity_score`, `communication_focus`). |
| **Structure & Resilience** | Modular code & Error Handling | Ensures separation of concerns and guarantees the application handles common failures (invalid URL, system dependency missing) gracefully. |

---

## 💻 Setup and Installation (Local Development)

### 0. Install System Prerequisites (FFmpeg / NodeJS)

This tool **relies on external binaries** for media processing. The Python code will fail immediately if these are not available.

* **Windows (via Chocolatey):** `choco install ffmpeg`
* **macOS (via Homebrew):** `brew install ffmpeg`
* **Linux (or Container):** Requires `ffmpeg` and `nodejs` (handled automatically during cloud deployment via `packages.txt`).

### 1. Clone the repository

```bash
git clone https://github.com/one-in-million/Video_Analyser
cd VideoAnalyser
2. Create and Activate Virtual Environment
Bash

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
3. Install Python Dependencies
Bash

pip install -r requirements.txt
4. Configure API Key (Local Testing)
The application uses Streamlit's secrets management (st.secrets). For local testing, create a directory and file named .streamlit/secrets.toml in the root of your project and add your key:

Ini, TOML

# .streamlit/secrets.toml
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
5. Run the Application
Bash

streamlit run app.py
🚀 Cloud Deployment (Streamlit Community Cloud)
This application is fully configured for easy, one-click deployment using Streamlit Community Cloud, which handles the complex system dependencies.

Deployment Prerequisites
Ensure your GitHub repository contains these three essential files:

app.py (Your main Streamlit application code).

requirements.txt (All Python packages).

packages.txt (The system dependencies required by yt-dlp):

# packages.txt
ffmpeg
nodejs
Steps to Deploy
Commit and Push: Ensure all updated files (especially packages.txt) are committed and pushed to your public GitHub repository.

Go to Streamlit Cloud: Select "New App" and choose your repository and branch.

Set Secrets: Under Advanced settings, use the Secrets section to securely set your API key:

Key: GEMINI_API_KEY

Value: Your actual Gemini API Key

Deploy: Click "Deploy!" Streamlit Cloud will automatically install the system dependencies from packages.txt and then run your application.