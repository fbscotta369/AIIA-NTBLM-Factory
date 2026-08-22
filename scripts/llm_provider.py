#!/usr/bin/env python3
"""
Content Generation with LLM Integration
Uses OpenRouter and other LLM providers to enhance content generation
"""

import os
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import configuration
import sys
sys.path.insert(0, str(Path(__file__).parent))
from content_harvest_p1 import (
    LLM_PROVIDERS, get_provider_api_key, get_env_var
)


@dataclass
class LLMRequest:
    """LLM request parameters"""
    prompt: str
    model: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    language: str = "en"
    system_prompt: Optional[str] = None


@dataclass
class LLMResponse:
    """LLM response container"""
    success: bool
    content: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    tokens_used: int = 0
    duration_ms: int = 0
    error: Optional[str] = None


class LLMProviderClient:
    """Client for LLM providers with fallback support"""
    
    def __init__(self, primary_provider: str = "openrouter"):
        self.primary_provider = primary_provider
        self.providers = LLM_PROVIDERS
        
    def generate_content(self, request: LLMRequest) -> LLMResponse:
        """Generate content using available providers with fallback"""
        last_error = None
        
        # Try primary provider first
        providers_to_try = [self.primary_provider]
        
        # Add fallback providers
        if self.primary_provider == "openrouter":
            providers_to_try.extend(["direct"])
        
        for provider_name in providers_to_try:
            config = self.providers.get(provider_name)
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
        
        return LLMResponse(
            success=False,
            error=last_error or "All providers failed"
        )
    
    def _call_provider(self, provider_name: str, config: Dict, 
                       api_key: str, request: LLMRequest) -> LLMResponse:
        """Call specific LLM provider"""
        
        if provider_name == "openrouter":
            return self._call_openrouter(config, api_key, request)
        elif provider_name == "direct":
            return self._call_direct(config, api_key, request)
        else:
            return LLMResponse(success=False, error=f"Unknown provider: {provider_name}")
    
    def _call_openrouter(self, config: Dict, api_key: str, 
                         request: LLMRequest) -> LLMResponse:
        """Generate content using OpenRouter API"""
        model = request.model or config.get("default_model")
        
        url = f"{config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AIIA-NTBLM-Factory",
            "X-Title": "AIIA-NTBLM-Factory"
        }
        
        # Build messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        start = time.time()
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if resp.status_code == 200:
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            
            return LLMResponse(
                success=True,
                content=content,
                provider="openrouter",
                model=model,
                tokens_used=usage.get("total_tokens", 0),
                duration_ms=int((time.time() - start) * 1000)
            )
        elif resp.status_code == 429:
            return LLMResponse(
                success=False,
                error="Rate limit exceeded (429)",
                provider="openrouter",
                model=model
            )
        else:
            return LLMResponse(
                success=False,
                error=f"OpenRouter error: {resp.status_code} - {resp.text[:200]}",
                provider="openrouter",
                model=model
            )
    
    def _call_direct(self, config: Dict, api_key: str, 
                     request: LLMRequest) -> LLMResponse:
        """Try direct providers (OpenAI, Anthropic, Google) as fallback"""
        # Try OpenAI first
        openai_config = config.get("providers", {}).get("openai", {})
        openai_key = api_key  # Use same key for simplicity in demo
        
        if openai_key:
            return self._call_openai_direct(openai_config, openai_key, request)
        
        # Try Anthropic
        anthropic_config = config.get("providers", {}).get("anthropic", {})
        # Anthropic uses different auth (x-api-key header)
        
        return LLMResponse(success=False, error="No direct providers configured")


def enhance_content_with_llm(content: Dict[str, Any], language: str,
                             provider_client: LLMProviderClient) -> Dict[str, Any]:
    """Enhance content sections using LLM"""
    
    for section in content.get("sections", []):
        # Create enhancement prompt
        prompt = f"""
Please enhance and expand the following content section. Make it more detailed, engaging, and educational.
Add practical examples, key takeaways, and ensure it's well-structured.

Original content:
{section.get('content', '')}

Language: {language}
Tone: Educational, professional, engaging
Target audience: Self-learners interested in AI

Please provide the enhanced version:
"""
        
        response = provider_client.generate_content(LLMRequest(
            prompt=prompt,
            language=language,
            system_prompt="You are an expert educator and content creator. Write clear, engaging educational content."
        ))
        
        if response.success:
            section["enhanced_content"] = response.content
            section["enhanced_by"] = f"{response.provider}/{response.model}"
            print(f"  ✅ Enhanced section: {section['title'][:30]}...")
        else:
            print(f"  ⚠️  Failed to enhance section: {section['title'][:30]}...")
            section["enhanced_content"] = section.get("content", "")
    
    return content


if __name__ == "__main__":
    # Demo test
    print("🤖 LLM Provider Integration Test")
    
    client = LLMProviderClient(primary_provider="openrouter")
    
    test_request = LLMRequest(
        prompt="Write a short introduction about learning AI in 2025. Keep it under 200 words.",
        model="google/gemini-2.0-flash-001"
    )
    
    result = client.generate_content(test_request)
    
    if result.success:
        print(f"✅ Content generated: {result.content[:100]}...")
        print(f"   Provider: {result.provider}")
        print(f"   Model: {result.model}")
        print(f"   Tokens: {result.tokens_used}")
    else:
        print(f"❌ Failed: {result.error}")
        print("   (This is expected if no API keys are configured)")