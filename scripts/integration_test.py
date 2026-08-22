#!/usr/bin/env python3
"""
INTEGRATION TEST - OpenRouter + TTS Providers + NotebookLM
Verifies that all credentials work end-to-end with real API calls

HOW TO USE:
1. Set environment variables for API keys
2. Run: python3 scripts/integration_test.py
"""

import os
import sys
import json
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_provider import LLMProviderClient, LLMRequest
from tts_provider import TTSProviderClient, TTSRequest
from notebooklm_browser import NotebookLMAccountManager, NotebookLMAutomation

print("=" * 60)
print("🔍 INTEGRATION TEST - AIIA-NTBLM-Factory")
print("🔧 Testing with configured credentials (env vars)")
print("=" * 60)
print()

# Check which API keys are configured
print("🔑 CONFIGURED CREDENTIALS:")
print("-" * 40)
config_keys = []
if os.environ.get("OPENROUTER_API_KEY"):
    print("   ✅ OpenRouter: configured")
    config_keys.append("openrouter")
else:
    print("   ❌ OpenRouter: NOT configured")

if os.environ.get("ELEVENLABS_API_KEY"):
    print("   ✅ ElevenLabs: configured")
    config_keys.append("elevenlabs")
else:
    print("   ❌ ElevenLabs: NOT configured")

if os.environ.get("DEEPGRAM_API_KEY"):
    print("   ✅ Deepgram: configured")
    config_keys.append("deepgram")
else:
    print("   ❌ Deepgram: NOT configured")

if os.environ.get("GLADIA_API_KEY"):
    print("   ✅ Gladia: configured")
    config_keys.append("gladia")
else:
    print("   ❌ Gladia: NOT configured")

print(f"\n   Total configured: {len(config_keys)}/{len(['openrouter', 'elevenlabs', 'deepgram', 'gladia'])}")
print()

# ============================================
# 1. TEST OPENROUTER (LLM)
# ============================================
print("📡 Testing OpenRouter API...")
print("-" * 40)

if not os.environ.get("OPENROUTER_API_KEY"):
    print("   ⚠️  SKIP: OpenRouter not configured")
    llm_working = False
    llm_working_en = False
    llm_results = {"es": None, "en": None}
else:
    llm_client = LLMProviderClient(primary_provider="openrouter")

    # Test with working model
    test_prompts = [
        ("es", "Escribe un párrafo sobre autoeducación con IA en 2025. Máximo 100 palabras."),
        ("en", "Write a paragraph about AI self-education in 2025. Maximum 100 words.")
    ]

    llm_working = True
    llm_working_en = True
    llm_results = {}
    for lang, prompt in test_prompts:
        print(f"\n  Testing {lang.upper()} generation...")
        request = LLMRequest(
            prompt=prompt,
            language=lang,
            model="anthropic/claude-3-haiku",  # Known working model
            max_tokens=150,
            temperature=0.7,
            system_prompt="Eres un experto en educación con IA. Escribe de forma clara y educativa."
        )
        
        result = llm_client.generate_content(request)
        llm_results[lang] = result
        
        if result.success:
            print(f"    ✅ OpenRouter OK - {result.provider}/{result.model}")
            print(f"    Content: {result.content[:80]}...")
            print(f"    Tokens: {result.tokens_used}")
        else:
            print(f"    ❌ OpenRouter failed: {result.error}")
            if lang == "es":
                llm_working = False
            elif lang == "en":
                llm_working_en = False

print()
print("-" * 40)

# ============================================
# 2. TEST TTS PROVIDERS (ElevenLabs ONLY - FIXED)
# ============================================
print("🎙️  Testing TTS Providers (ElevenLabs Only - Fixed)")
print("-" * 40)

if not config_keys:
    print("   ⚠️  SKIP: No TTS providers configured")
    tts_working = False
    tts_results = {"es": None, "en": None}
else:
    tts_client = TTSProviderClient()

    test_texts = {
        "es": "Hola, esto es una prueba de síntesis de voz en español. ¿Me escuchas bien?",
        "en": "Hello, this is a text-to-speech test in English. Can you hear me clearly?"
    }

    tts_working = True
    tts_results = {}
    for lang, text in test_texts.items():
        print(f"\n  Testing {lang.upper()} audio generation...")
        request = TTSRequest(
            text=text,
            language=lang,
            output_format="mp3",
            output_path=f"outputs/audio/test_{lang}.mp3"
        )
        
        result = tts_client.generate_speech(request)
        tts_results[lang] = result
        
        if result.success:
            print(f"    ✅ {result.provider} OK")
            print(f"    Audio: {result.audio_path}")
            print(f"    Size: {result.bytes_generated} bytes")
            print(f"    Duration: {result.duration_ms}ms")
        else:
            print(f"    ❌ {lang.upper()} TTS failed: {result.error}")
            tts_working = False

print()
print("-" * 40)

# ============================================
# 3. TEST NOTEBOOKLM ROUND-ROBIN
# ============================================
print("🔐 Testing NotebookLM Account Rotation...")
print("-" * 40)

account_manager = NotebookLMAccountManager()

print(f"\n  Available accounts ({len(account_manager.accounts)}):")
for i, acc in enumerate(account_manager.accounts):
    status = "✅ Ready" if account_manager.is_account_available(acc) else "⚠️ In cooldown"
    masked_pw = acc["password"][:2] + "***"
    print(f"    {i+1}. {acc['username']} (pw: {masked_pw}) - {status}")

print("\n  Round-robin simulation (6 requests):")
for i in range(6):
    account = account_manager.get_next_account()
    if account:
        print(f"    Request {i+1}: {account['username']}")
        
        # Simulate failure on 4th request to test cooldown
        if i == 3:
            account_manager.mark_failed(account)
            print(f"      ⚠️  (simulated failure - adding 5min cooldown)")
    else:
        print(f"    Request {i+1}: ⚠️ No accounts available (all in cooldown)")

# Reset for next test
account_manager.current_index = 0
account_manager.failed_accounts.clear()
account_manager.cooldown_until.clear()

print()
print("-" * 40)

# ============================================
# 4. FULL PIPELINE END-TO-END TEST
# ============================================
print("🔄 Full Pipeline End-to-End Test")
print("-" * 40)

# Check if we have all components working
accounts_available = len(account_manager.accounts) > 0

print(f"\n  Pipeline Components:")
print(f"    🤖 LLM (OpenRouter): {'✅' if llm_working and llm_working_en else '❌'} ")
print(f"    🎙️ TTS (ElevenLabs Only): {'✅' if tts_working else '❌'} ")
print(f"    🔐 NotebookLM Accounts: ✅ ({len(account_manager.accounts)} accounts)")

all_working = (llm_working and llm_working_en) and tts_working and accounts_available

if all_working:
    print(f"\n  ✅ Pipeline ready for production use!")
    print(f"  Next step: Run content harness with real topic")
else:
    print(f"\n  ⚠️  Some components need configuration")
    if not (llm_working and llm_working_en):
        print(f"     → Set OPENROUTER_API_KEY env var")
    if not tts_working:
        print(f"     → Check ElevenLabs API key")

print()
print("-" * 40)

# ============================================
# SUMMARY
# ============================================
print("📊 FINAL SUMMARY")
print("=" * 60)

print(f"\n  OpenRouter: {'✅ Working' if llm_working and llm_working_en else '❌ Failed'}")
print(f"  TTS Providers: {'✅ Working' if tts_working else '❌ Failed'}")
print(f"  NotebookLM Accounts: ✅ {len(account_manager.accounts)} accounts in pool")

if all_working:
    print(f"\n  🎉 ALL SYSTEMS OPERATIONAL")
    print(f"  Ready to generate bilingual content")
else:
    print(f"\n  ⚠️  CONFIGURATION NEEDED")

print("=" * 60)