#!/usr/bin/env python3
"""
FINAL INTEGRATION TEST - OpenRouter + ElevenLabs + NotebookLM
Complete validation of the working AIIA-NTBLM-Factory pipeline
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🔍 FINAL INTEGRATION TEST - AIIA-NTBLM-Factory - MINIMAL MODE")
print("=" * 80)
print()

# ============================================
# CHECK CREDENTIALS CONFIGURATION
# ============================================
print("🔑 CHECKING CREDENTIALS CONFIGURATION:")
print("-" * 50)

config_status = {}

# OpenRouter
if os.environ.get("OPENROUTER_API_KEY"):
    print("   ✅ OpenRouter: Configured")
    config_status["openrouter"] = True
else:
    print("   ❌ OpenRouter: NOT configured")
    config_status["openrouter"] = False

# ElevenLabs  
if os.environ.get("ELEVENLABS_API_KEY"):
    print("   ✅ ElevenLabs: Configured")
    config_status["elevenlabs"] = True
else:
    print("   ❌ ElevenLabs: NOT configured")
    config_status["elevenlabs"] = False

# NotebookLM accounts
from notebooklm_browser import NotebookLMAccountManager
account_manager = NotebookLMAccountManager()
if account_manager.accounts:
    print(f"   ✅ NotebookLM: Configured ({len(account_manager.accounts)} accounts)")
    config_status["notebooklm"] = True
else:
    print("   ❌ NotebookLM: NOT configured")
    config_status["notebooklm"] = False

print(f"\n   Summary: {sum(config_status.values())}/{len(config_status)} services configured")
print()

# ============================================
# QUICK LLM TEST (OpenRouter only)
# ============================================
print("📡 QUICK LLM TEST (OpenRouter - Claude 3 Haiku):")
print("-" * 50)

if not config_status.get("openrouter"):
    print("   ⚠️  SKIP: OpenRouter not configured")
    llm_ok = False
else:
    from llm_provider import LLMProviderClient, LLMRequest
    
    llm_client = LLMProviderClient(primary_provider="openrouter")
    
    test_prompt = "How to self-educate with AI using the Dan Martell method? Max 50 words."
    request = LLMRequest(
        prompt=test_prompt,
        language="en",
        model="anthropic/claude-3-haiku",
        max_tokens=100,
        temperature=0.7
    )
    
    result = llm_client.generate_content(request)
    
    if result.success:
        print(f"   ✅ OpenRouter working: {result.provider}")
        print(f"   Response: {result.content[:80]}...")
        llm_ok = True
    else:
        print(f"   ❌ OpenRouter failed: {result.error}")
        llm_ok = False

print()

# ============================================
# QUICK TTS TEST (ElevenLabs only)
# ============================================
print("🎙️ QUICK TTS TEST (ElevenLabs Only):")
print("-" * 50)

if not config_status.get("elevenlabs"):
    print("   ⚠️  SKIP: ElevenLabs not configured")
    tts_ok = False
else:
    from tts_provider import TTSProviderClient, TTSRequest
    
    tts_client = TTSProviderClient()
    
    test_text = "Hello, this is a test of the ElevenLabs TTS integration for the AIIA-NTBLM-Factory pipeline."
    request = TTSRequest(
        text=test_text,
        language="en",
        output_format="mp3",
        output_path="outputs/audio/final_test.mp3"
    )
    
    result = tts_client.generate_speech(request)
    
    if result.success:
        print(f"   ✅ ElevenLabs working: {result.provider}")
        print(f"   Audio saved: {result.audio_path} ({result.bytes_generated} bytes)")
        tts_ok = True
    else:
        print(f"   ❌ ElevenLabs failed: {result.error}")
        tts_ok = False

print()

# ============================================
# QUICK NOTEBOOKLM TEST (Account rotation)
# ============================================
print("🔐 QUICK NOTEBOOKLM TEST (Account Rotation):")
print("-" * 50)

account_manager = NotebookLMAccountManager()
if config_status.get("notebooklm") and account_manager.accounts:
    print(f"   ✅ Account pool ready: {len(account_manager.accounts)} accounts")
    
    # Test round-robin
    for i in range(min(3, len(account_manager.accounts))):
        account = account_manager.get_next_account()
        print(f"   Account {i+1}: {account['username']}")
    
    account_ok = True
else:
    print("   ❌ NotebookLM not configured")
    account_ok = False

print()

# ============================================
# FINAL ASSESSMENT
# ============================================
print("📊 FINAL INTEGRATION ASSESSMENT:")
print("=" * 80)

components = {
    "OpenRouter (LLM)": llm_ok,
    "ElevenLabs (TTS)": tts_ok,
    "NotebookLM (Accounts)": account_ok
}

all_ok = True
for component, status in components.items():
    icon = "✅" if status else "❌"
    print(f"   {icon} {component}: {'WORKING' if status else 'FAILED'}")
    if not status:
        all_ok = False

print()

if all_ok:
    print("🎉 ALL INTEGRATIONS SUCCESSFUL!")
    print("   The AIIA-NTBLM-Factory pipeline is ready for production.")
    print("   Ready to process: 'Cómo auto-educarse con IA. El método Dan Martell'")
    print("   in Spanish (LATAM female voice) and English (UK female voice).")
else:
    print("⚠️ INTEGRATION INCOMPLETE")
    print("   Some services need configuration:")
    for component, status in components.items():
        if not status:
            if component == "OpenRouter (LLM)":
                print("     • Set OPENROUTER_API_KEY environment variable")
            elif component == "ElevenLabs (TTS)":
                print("     • Set ELEVENLABS_API_KEY environment variable")
            elif component == "NotebookLM (Accounts)":
                print("     • Configure NotebookLM accounts in .env")

print("=" * 80)
print("Test completed at:", os.environ.get("PWD", "/home/fb/AIIA-NTBLM-Factory"))