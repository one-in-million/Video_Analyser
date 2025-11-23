import streamlit as st
import os
import json # Ensure json is imported for error handling
from dotenv import load_dotenv
from google import genai
from core.analysis_engine import process_video_insights, CommunicationAnalysis # Ensure this import is correct

# --- Configuration & Initialization ---

# 1. Load environment variables (API Key)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check for API Key and initialize client
if GEMINI_API_KEY:
    try:
        # Ensure the client is only initialized once
        @st.cache_resource
        def get_gemini_client():
            return genai.Client(api_key=GEMINI_API_KEY)
        
        gemini_client = get_gemini_client()
        st.session_state['client_ready'] = True
    except Exception as e:
        st.error(f"Failed to initialize Gemini Client: {e}")
        st.session_state['client_ready'] = False
else:
    st.session_state['client_ready'] = False
    
# --- Streamlit UI Components ---

st.set_page_config(
    page_title="Video Insight Analyzer",
    layout="wide", # Use 'wide' layout for better visualization of results
    initial_sidebar_state="auto"
)

# Custom header using markdown and columns
col_logo, col_title = st.columns([1, 6])

with col_logo:
    # A simple placeholder icon
    st.image("https://placehold.co/100x100/31333F/90EE90?text=AI", width=70)

with col_title:
    st.title("Video Insight Analyzer")
    st.markdown(
        """
        Extract professional communication metrics from a public video URL using Gemini's multimodal capabilities. 
        Focus is on **backend proficiency** and **reliable, structured data extraction.**
        """
    )
    st.divider()

# 1. API Key Warning
if not st.session_state.get('client_ready'):
    st.error("🚨 **Configuration Error!** Please ensure you have set the `GEMINI_API_KEY` in your `.env` file and restarted the application.")
    st.stop()


# 2. User Input Section
st.subheader("🔗 1. Video Input")
video_url = st.text_input(
    "Paste Public Video URL (YouTube, Loom, etc.)",
    placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    key="video_url_input",
    label_visibility="collapsed"
)

# 3. Processing Logic
if st.button("Analyze Video Insights", type="primary", use_container_width=True) and video_url:
    
    if not video_url.startswith(("http://", "https://")):
        st.error("Please enter a valid URL starting with http:// or https://")
        st.stop()
        
    try:
        # Use st.spinner for a clean, non-intrusive loading indicator
        with st.spinner("Processing large video file... This may take a minute due to audio chunking and analysis."):
            
            # The main backend call (handles extraction, chunking, transcription, and final analysis)
            analysis: CommunicationAnalysis = process_video_insights(
                video_url=video_url, 
                client=gemini_client
            )

        # 4. Display Outputs (Professional Results Card)
        
        st.success("Analysis Complete! Insights Extracted:")
        st.subheader("✨ 2. Communication Insights")
        
        # --- Display Metrics using Columns ---
        col_focus, col_score = st.columns([3, 1])

        with col_focus:
            st.markdown("##### 🎯 Main Communication Focus")
            st.markdown(f"> **{analysis.communication_focus}**")
            
        with col_score:
            # Use st.metric for the core quantitative output
            st.metric(
                label="Clarity Score (0-100%)", 
                value=f"{analysis.clarity_score}%",
                delta="Key metric for fluency and structure.",
                delta_color="off"
            )

        st.markdown("---")

        # --- Display Full Transcript (Required for context/validation) ---
        st.subheader("📜 Full Transcript & Data Validation")
        st.markdown("The following text was generated via audio chunking and used for the final LLM analysis.")
        
        # --- MODIFIED SECTION FOR SCROLLING ---
        with st.expander("Expand to View Transcript", expanded=False):
            # Apply custom CSS to a div wrapper to enforce vertical scrolling (max height 400px)
            st.markdown(
                f"""
                <div style="height: 400px; overflow-y: scroll; border: 1px solid #444; padding: 10px; border-radius: 5px; background-color: #0E1117;">
                    <pre style="white-space: pre-wrap; font-family: monospace;">{analysis.transcript}</pre>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    except ConnectionError as e:
        st.error(f"**API Error:** {e}")
        st.markdown("The Gemini service is unavailable or the request timed out. Please wait a moment and try again.")
    except ValueError as e:
        st.error(f"**Video Processing Error:** {e}")
        st.markdown("The video URL may be invalid, private, or the required `ffmpeg` utility is not correctly installed/accessible in your PATH.")
    except Exception as e:
        st.exception(e)
        st.error(f"An unexpected error occurred: {e}")

# Footer for context
st.markdown("---")
st.caption("Backend built with Python, `yt-dlp`, `pydub`, and Google Gemini API.")