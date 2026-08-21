#!/usr/bin/env python3
"""
AIIA-NTBLM-Factory — Configuration
Central configuration management for the pipeline.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
ROOT = Path(__file__).parent.resolve()
load_dotenv(ROOT / ".env")

# =============================================================================
# API Keys
# =============================================================================
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# =============================================================================
# Google / NotebookLM
# =============================================================================
NOTEBOOKLM_EMAIL = "fbscotta@gmail.com"
NOTEBOOKLM_PASSWORD = os.environ.get("NOTEBOOKLM_PASSWORD", "")
NOTEBOOKLM_URL = "https://notebooklm.google.com"

# =============================================================================
# YouTube
# =============================================================================
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# =============================================================================
# ElevenLabs (TTS)
# =============================================================================
# Voice IDs for female voices
ELEVENLABS_VOICE_ES = "XbQXCjpM9k00zzSX8vD7"  # María (LatAm Spanish, female)
ELEVENLABS_VOICE_EN = "Thq69S6I3X0H6kVrBU9P"  # Alice (British English, female)

# =============================================================================
# Language Configuration
# =============================================================================
LANGUAGES = {
    "es": {
        "name": "Español (LatAm)",
        "voice": ELEVENLABS_VOICE_ES,
        "locale": "es-LA",
        "voice_gender": "female",
    },
    "en": {
        "name": "English (British)",
        "voice": ELEVENLABS_VOICE_EN,
        "locale": "en-GB",
        "voice_gender": "female",
    },
}

# =============================================================================
# Output
# =============================================================================
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", str(ROOT / "output"))
SITE_URL = os.environ.get("SITE_URL", "https://aiia-ntblm-factory.vercel.app")

# =============================================================================
# Supabase (optional — for tracking generated products)
# =============================================================================
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# =============================================================================
# Quality thresholds
# =============================================================================
QUALITY_THRESHOLDS = {
    "min_pdf_size_kb": 100,       # PDF must be > 100KB
    "min_audio_size_kb": 10,      # Audio must be > 10KB
    "min_video_duration_sec": 10, # Video must be > 10s
    "min_summary_length": 100,    # Summary must be > 100 chars
    "min_sections": 3,            # At least 3 sections in PDF
}

def validate_config():
    """Validate that required config is present. Returns (ok, missing)."""
    required = {
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "ELEVENLABS_API_KEY": ELEVENLABS_API_KEY,
        "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
        "NOTEBOOKLM_PASSWORD": NOTEBOOKLM_PASSWORD,
    }
    missing = [k for k, v in required.items() if not v]
    return len(missing) == 0, missing
