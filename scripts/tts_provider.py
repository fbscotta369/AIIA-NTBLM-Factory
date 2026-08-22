#!/usr/bin/env python3
"""
TTS Provider Integration Module
Handles text-to-speech generation using ElevenLabs (only provider that works)
"""

import os
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import configuration from part 1
import sys
sys.path.insert(0, str(Path(__file__).parent))
from content_harvest_p1 import (
    TTS_PROVIDERS, TTS_FALLBACK_ORDER, 
    get_provider_api_key, get_env_var
)


@dataclass
class TTSRequest:
    """Text-to-speech request parameters"""
    text: str
    language: str  # "es" or "en"
    output_format: str = "mp3"
    output_path: Optional[str] = None
    voice_id: Optional[str] = None
    model_id: Optional[str] = None
    speed: float = 1.0
    pitch: float = 1.0


@dataclass
class TTSResponse:
    """TTS response container"""
    success: bool
    audio_path: Optional[str] = None
    provider: Optional[str] = None
    duration_ms: int = 0
    error: Optional[str] = None
    bytes_generated: int = 0


class TTSProviderClient:
    """Client for TTS providers with fallback support"""
    
    def __init__(self, provider_order: List[str] = None):
        self.provider_order = provider_order or TTS_FALLBACK_ORDER
        self.provider_configs = TTS_PROVIDERS
        self.session = requests.Session()
        
    def generate_speech(self, request: TTSRequest) -> TTSResponse:
        """Generate speech using available providers with fallback"""
        last_error = None
        
        for provider_name in self.provider_order:
            config = self.provider_configs.get(provider_name)
            if not config:
                continue
            
            api_key = get_provider_api_key(provider_name)
            if not api_key:
                print(f"  ⚠️  {provider_name}: No API key configured")
                continue
            
            try:
                response = self._call_provider(
                    provider_name, config, api_key, request
                )
                
                if response.success:
                    return response
                    
            except Exception as e:
                last_error = str(e)
                print(f"  ⚠️  {provider_name} failed: {e}")
                continue
        
        return TTSResponse(
            success=False,
            error=last_error or "All providers failed"
        )
    
    def _call_provider(self, provider_name: str, config: Dict, 
                       api_key: str, request: TTSRequest) -> TTSResponse:
        """Call specific TTS provider"""
        
        if provider_name == "elevenlabs":
            return self._call_elevenlabs(config, api_key, request)
        elif provider_name == "deepgram":
            return self._call_deepgram(config, api_key, request)
        elif provider_name == "gladia":
            return self._call_gladia(config, api_key, request)
        elif provider_name == "google":
            return self._call_google(config, api_key, request)
        else:
            return TTSResponse(success=False, error=f"Unknown provider: {provider_name}")
    
    def _call_elevenlabs(self, config: Dict, api_key: str, 
                         request: TTSRequest) -> TTSResponse:
        """Generate speech using ElevenLabs API"""
        voice_id = request.voice_id or config["voices"].get(request.language)
        model_id = request.model_id or config.get("model", "eleven_multilingual_v2")
        
        url = f"{config['base_url']}/text-to-speech/{voice_id}"
        headers = {
            "Accept": f"audio/{request.output_format}",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        payload = {
            "text": request.text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0
            }
        }
        
        start = time.time()
        resp = self.session.post(url, headers=headers, json=payload, timeout=30)
        
        if resp.status_code == 200:
            audio_bytes = resp.content
            output_path = request.output_path or f"outputs/audio/{request.language}_{int(start)}.mp3"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            return TTSResponse(
                success=True,
                audio_path=output_path,
                provider="elevenlabs",
                duration_ms=int((time.time() - start) * 1000),
                bytes_generated=len(audio_bytes)
            )
        else:
            return TTSResponse(
                success=False,
                error=f"ElevenLabs error: {resp.status_code}",
                provider="elevenlabs"
            )
    
    def _call_deepgram(self, config: Dict, api_key: str, 
                       request: TTSRequest) -> TTSResponse:
        """Generate speech using Deepgram API"""
        voice = request.voice_id or config["voices"].get(request.language)
        
        # Deepgram uses model parameter for voice selection
        model = request.model_id or config["models"].get(request.language, "aura-asteria-en")
        
        url = f"{config['base_url']}/tts?model={model}&language={request.language}"
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": request.text,
            "speed": request.speed
        }
        
        start = time.time()
        resp = self.session.post(url, headers=headers, json=payload, timeout=30)
        
        if resp.status_code == 200:
            audio_bytes = resp.content
            output_path = request.output_path or f"outputs/audio/{request.language}_{int(start)}.mp3"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            return TTSResponse(
                success=True,
                audio_path=output_path,
                provider="deepgram",
                duration_ms=int((time.time() - start) * 1000),
                bytes_generated=len(audio_bytes)
            )
        else:
            return TTSResponse(
                success=False,
                error=f"Deepgram error: {resp.status_code}",
                provider="deepgram"
            )
    
    def _call_gladia(self, config: Dict, api_key: str, 
                     request: TTSRequest) -> TTSResponse:
        """Generate speech using Gladia API"""
        # Gladia uses a different API structure
        url = f"{config['base_url']}/text-to-speech"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": request.text,
            "language": "es" if request.language == "es" else "en",
            "output_format": request.output_format
        }
        
        start = time.time()
        resp = self.session.post(url, headers=headers, json=payload, timeout=30)
        
        if resp.status_code == 200:
            # Gladia returns JSON with audio URL, download it
            data = resp.json()
            audio_url = data.get("url") or data.get("audio_url")
            if audio_url:
                audio_resp = self.session.get(audio_url, timeout=30)
                audio_bytes = audio_resp.content
            else:
                audio_bytes = resp.content
            
            output_path = request.output_path or f"outputs/audio/{request.language}_{int(start)}.mp3"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            return TTSResponse(
                success=True,
                audio_path=output_path,
                provider="gladia",
                duration_ms=int((time.time() - start) * 1000),
                bytes_generated=len(audio_bytes)
            )
        else:
            return TTSResponse(
                success=False,
                error=f"Gladia error: {resp.status_code}",
                provider="gladia"
            )
    
    def _call_google(self, config: Dict, api_key: str, 
                     request: TTSRequest) -> TTSResponse:
        """Generate speech using Google Cloud TTS"""
        voice = request.voice_id or config["voices"].get(request.language)
        language_code = "es-MX" if request.language == "es" else "en-GB"
        
        url = f"{config['base_url']}/text:synthesize?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "input": {"text": request.text},
            "voice": {
                "languageCode": language_code,
                "name": voice,
                "ssmlGender": "FEMALE"
            },
            "audioConfig": {
                "audioEncoding": request.output_format.upper(),
                "speakingRate": request.speed,
                "pitch": request.pitch
            }
        }
        
        start = time.time()
        resp = self.session.post(url, headers=headers, json=payload, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            audio_content = data.get("audioContent", "")
            
            # Base64 decode
            import base64
            audio_bytes = base64.b64decode(audio_content)
            
            output_path = request.output_path or f"outputs/audio/{request.language}_{int(start)}.mp3"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            return TTSResponse(
                success=True,
                audio_path=output_path,
                provider="google",
                duration_ms=int((time.time() - start) * 1000),
                bytes_generated=len(audio_bytes)
            )
        else:
            return TTSResponse(
                success=False,
                error=f"Google TTS error: {resp.status_code}",
                provider="google"
            )


def generate_audio_for_content(content: Dict[str, Any], language: str, 
                               output_dir: str = "outputs/audio") -> TTSResponse:
    """Generate audio for a content section using TTS"""
    client = TTSProviderClient()
    
    # Combine all section content for audio generation
    full_text = ""
    for section in content.get("sections", []):
        full_text += section.get("content", "") + "\n\n"
    
    if not full_text:
        return TTSResponse(success=False, error="No content to convert to audio")
    
    request = TTSRequest(
        text=full_text,
        language=language,
        output_path=f"{output_dir}/{language}_full.mp3"
    )
    
    return client.generate_speech(request)


if __name__ == "__main__":
    # Demo test
    print("🔊 TTS Provider Integration Test")
    
    # Test with sample text
    test_request = TTSRequest(
        text="Hola, esto es una prueba de síntesis de voz en español.",
        language="es"
    )
    
    client = TTSProviderClient()
    result = client.generate_speech(test_request)
    
    if result.success:
        print(f"✅ Audio generated: {result.audio_path}")
        print(f"   Provider: {result.provider}")
        print(f"   Size: {result.bytes_generated} bytes")
    else:
        print(f"❌ Failed: {result.error}")
        print("   (This is expected if no API keys are configured)")