#!/usr/bin/env python3
"""
NotebookLM Integration - Main Content Harvesting Script
Extracts and processes content from NotebookLM for bilingual digital products
Part 1: Imports and Configuration
"""

import argparse
import json
import os
import re
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional

# === TTS PROVIDER CONFIGURATION ===
# NOTE: In production, load from environment variables or secure config
# NEVER hardcode credentials in repo files

TTS_PROVIDERS = {
    "elevenlabs": {
        "api_key_env": "ELEVENLABS_API_KEY",
        "base_url": "https://api.elevenlabs.io/v1",
        "model": "eleven_multilingual_v2",
        # Best voices for educational content (tested working)
        "voices": {
            "es": "EXAVITQu4vr4xnSDxMaL",  # Sarah - Mature, Reassuring, Confident (Latin American Spanish)
            "en": "Xb7hH8MSUJpSbSDYk0k2"   # Alice - Clear, Engaging Educator (English UK)
        },
        "alternative_voices": {
            "es": ["EXAVITQu4vr4xnSDxMaL", "Fg6lYND2Nt1Xw4Wk8LJk"],  # Sarah, plus backups
            "en": ["Xb7hH8MSUJpSbSDYk0k2", "XrExE9yKIg1WjnnlVkGX"]   # Alice, Matilda
        }
    }
    # Deepgram - SKIP (TTS endpoint not working)
    # Gladia - SKIP (DNS resolution issues)
    # Google - SKIP (needs separate Cloud API key)
}

# Default TTS provider selection order (round-robin fallback)
# ElevenLabs first (best quality), then Deepgram (reliable), then Google, Gladia last
TTS_FALLBACK_ORDER = ["elevenlabs"]

# === LLM PROVIDER CONFIGURATION ===
LLM_PROVIDERS = {
    "openrouter": {
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "anthropic/claude-3-haiku",
        "fallback_models": [
            "anthropic/claude-3-haiku",
            "meta-llama/llama-3.1-8b-instruct",
            "openai/gpt-3.5-turbo"
        ]
    },
    "direct": {
        "providers": {
            "openai": {"base_url": "https://api.openai.com/v1"},
            "anthropic": {"base_url": "https://api.anthropic.com/v1"},
            "google": {"base_url": "https://generativelanguage.googleapis.com/v1"}
        }
    }
}

# === GOOGLE ACCOUNTS FOR NOTEBOOKLM (ROUND ROBIN) ===
# NOTE: These are used only in memory during session, never stored in repo
NOTEBOOKLM_ACCOUNTS = [
    {"username": "f4kub4lt4", "password": "Lmmjvsd69!."},
    {"username": "B4lth4z4r.369", "password": "Lmmjvsd69!."},
    {"username": "baltazar.scotta.369", "password": "Lmmjvsd369!."}
]

# Active account index for round-robin
_active_account_index = 0


def get_next_notebooklm_account() -> Dict[str, str]:
    """Get next Google account for NotebookLM (round-robin)"""
    global _active_account_index
    account = NOTEBOOKLM_ACCOUNTS[_active_account_index]
    _active_account_index = (_active_account_index + 1) % len(NOTEBOOKLM_ACCOUNTS)
    return account


def reset_account_rotation():
    """Reset round-robin to start from first account"""
    global _active_account_index
    _active_account_index = 0


# === DEFAULTS ===
DEFAULT_OUTPUT_DIR = "outputs"
DEFAULT_LANGUAGES = ["es", "en"]
SUPPORTED_LANGUAGES = {
    "es": "es-MX-DaliaNeural",
    "en": "en-GB-LibbyNeural"
}

# Language name mapping
LANGUAGE_NAMES = {
    "es": "es-LATAM",
    "en": "en-UK"
}

# Outline keys
OUTLINE_KEYS = {
    "es": "spanish",
    "en": "english"
}


def validate_languages(languages: list) -> list:
    """Validate language codes are supported"""
    valid = []
    for lang in languages:
        if lang in SUPPORTED_LANGUAGES:
            valid.append(lang)
        else:
            print(f"Warning: Unsupported language '{lang}', skipping")
    return valid


def normalize_output_dir(output_dir: str) -> Path:
    """Normalize and create output directory"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_env_var(name: str, default: str = "") -> str:
    """Get environment variable with default"""
    return os.environ.get(name, default)


def get_provider_api_key(provider: str) -> str:
    """Get API key for a provider from environment"""
    provider_config = TTS_PROVIDERS.get(provider) or LLM_PROVIDERS.get(provider)
    if provider_config and "api_key_env" in provider_config:
        return get_env_var(provider_config["api_key_env"], "")
    return ""


print(f"✅ Part 1 loaded: Imports and Configuration")