#!/usr/bin/env python3
"""
ElevenLabs Voice Discovery - Test all 23 voices for ES/EN TTS
Find working voice IDs for Spanish and English female voices
"""

import os
import sys
import json
import requests
from pathlib import Path

# Setup
os.environ['ELEVENLABS_API_KEY'] = 'sk_d846444de1fbe58dbaa62f5e96014913d543dfde078a2ff3'
API_KEY = os.environ['ELEVENLABS_API_KEY']

print("=" * 70)
print("🎤 ELEVENLABS VOICE DISCOVERY - Testing All 23 Voices")
print("=" * 70)
print()

# Get all voices
url = "https://api.elevenlabs.io/v1/voices"
headers = {"xi-api-key": API_KEY}
resp = requests.get(url, headers=headers, timeout=15)
voices_data = resp.json()

# Define test texts
TEST_TEXTS = {
    "es": "Hola, estoy probando esta voz en español. ¿Puedes oírme claro?",
    "en": "Hello, I am testing this voice in English. Can you hear me clearly?"
}

# Results tracking
working_voices = []
failed_voices = []

print("Testing each voice with both Spanish and English text...")
print("-" * 70)

for idx, voice in enumerate(voices_data['voices']):
    name = voice.get('name', 'Unknown')
    voice_id = voice.get('voice_id', '')
    
    print(f"\n[{idx+1}/23] {name}")
    print(f"     Voice ID: {voice_id}")
    
    voice_results = {"es": None, "en": None}
    
    # Test each language
    for lang, text in TEST_TEXTS.items():
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        tts_headers = {
            "xi-api-key": API_KEY,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json"
        }
        tts_payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2"
        }
        
        try:
            resp = requests.post(tts_url, headers=tts_headers, json=tts_payload, timeout=15)
            
            if resp.status_code == 200:
                audio_bytes = len(resp.content)
                print(f"     ✅ {lang.upper()}: OK ({audio_bytes} bytes)")
                voice_results[lang] = "success"
                
                # Save audio for successful voices
                out_path = Path(f"outputs/audio/voice_test_{voice_id}_{lang}.mp3")
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(resp.content)
            elif resp.status_code == 404:
                error_detail = resp.json().get('detail', {}).get('message', 'Voice not found')
                print(f"     ❌ {lang.upper()}: 404 - {error_detail[:60]}")
                voice_results[lang] = "voice_not_found"
            elif resp.status_code == 403:
                error_detail = resp.json().get('detail', {}).get('message', 'Forbidden')
                print(f"     ⚠️  {lang.upper()}: 403 - {error_detail[:60]}")
                voice_results[lang] = "forbidden"
            else:
                print(f"     ❌ {lang.upper()}: {resp.status_code}")
                voice_results[lang] = f"error_{resp.status_code}"
                
        except Exception as e:
            print(f"     ❌ {lang.upper()}: Exception - {str(e)[:60]}")
            voice_results[lang] = "exception"
    
    # Track results
    if voice_results["es"] == "success" and voice_results["en"] == "success":
        working_voices.append({"name": name, "voice_id": voice_id, "results": voice_results})
        print(f"     🎯 FULLY WORKING (ES + EN)")
    elif voice_results["es"] == "success":
        working_voices.append({"name": name, "voice_id": voice_id, "results": voice_results, "lang": "es"})
        print(f"     🎯 Works for SPANISH only")
    elif voice_results["en"] == "success":
        working_voices.append({"name": name, "voice_id": voice_id, "results": voice_results, "lang": "en"})
        print(f"     🎯 Works for ENGLISH only")
    else:
        failed_voices.append({"name": name, "voice_id": voice_id, "results": voice_results})

# ============================================
# SUMMARY
# ============================================
print()
print("=" * 70)
print("📊 RESULTS SUMMARY")
print("=" * 70)

print(f"\n✅ Working voices: {len(working_voices)}/23")
print(f"❌ Failed voices: {len(failed_voices)}/23")

print("\n--- VOICES WORKING FOR BOTH ES + EN ---")
for v in working_voices:
    if v.get("results", {}).get("es") == "success" and v.get("results", {}).get("en") == "success":
        print(f"  • {v['name']} (ID: {v['voice_id']})")

print("\n--- VOICES WORKING FOR SPANISH ONLY ---")
for v in working_voices:
    if v.get("results", {}).get("es") == "success" and v.get("results", {}).get("en") != "success":
        print(f"  • {v['name']} (ID: {v['voice_id']})")

print("\n--- VOICES WORKING FOR ENGLISH ONLY ---")
for v in working_voices:
    if v.get("results", {}).get("en") == "success" and v.get("results", {}).get("es") != "success":
        print(f"  • {v['name']} (ID: {v['voice_id']})")

print("\n--- FAILED VOICES ---")
for v in failed_voices:
    es_result = v['results'].get('es', 'N/A')
    en_result = v['results'].get('en', 'N/A')
    print(f"  • {v['name']} (ES: {es_result}, EN: {en_result})")

print()
print("=" * 70)
print("📝 RECOMMENDATIONS")
print("=" * 70)

# Find best candidates
both_working = [v for v in working_voices 
                if v.get("results", {}).get("es") == "success" 
                and v.get("results", {}).get("en") == "success"]

if both_working:
    print("\n✅ Best candidates (work for both languages):")
    for v in both_working:
        print(f"   → {v['name']} | ID: {v['voice_id']}")
else:
    es_only = [v for v in working_voices if v.get("lang") == "es"]
    en_only = [v for v in working_voices if v.get("lang") == "en"]
    
    print("\n⚠️  No voices work for both languages")
    if es_only:
        print(f"\n   Spanish voices ({len(es_only)}):")
        for v in es_only:
            print(f"   → {v['name']} | ID: {v['voice_id']}")
    if en_only:
        print(f"\n   English voices ({len(en_only)}):")
        for v in en_only:
            print(f"   → {v['name']} | ID: {v['voice_id']}")

print()
print("=" * 70)
print("✅ Voice discovery complete")
print("=" * 70)
