#!/usr/bin/env python3
"""
NotebookLM Content Harvesting Script - Part 3
Content generation and bilingual outline creation
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import from previous parts
sys.path.insert(0, str(Path(__file__).parent))
from content_harvest_p1 import (
    LLM_PROVIDERS, get_provider_api_key, get_env_var,
    TTS_PROVIDERS, TTS_FALLBACK_ORDER
)

# Check if LLM and TTS are available
HAS_LLM = False
HAS_TTS = False

# Try to import LLM client
try:
    import llm_provider as _llm
    HAS_LLM = True
except ImportError:
    pass

# Try to import TTS client
try:
    import tts_provider as _tts
    HAS_TTS = True
except ImportError:
    pass


def _call_llm_generate(client, prompt: str, model: str, language: str, system_prompt: str) -> Optional[str]:
    """Call LLM to generate content"""
    if not HAS_LLM or client is None:
        return None
    
    try:
        from llm_provider import LLMRequest
        req = LLMRequest(
            prompt=prompt,
            model=model,
            max_tokens=2000,
            temperature=0.7,
            language=language,
            system_prompt=system_prompt
        )
        result = client.generate_content(req)
        if result.success and result.content:
            return result.content
    except Exception as e:
        print(f"   ⚠️  LLM call failed: {e}")
    return None


def _call_tts_generate(client, text: str, language: str, output_path: str) -> Optional[Dict]:
    """Call TTS to generate audio"""
    if not HAS_TTS or client is None:
        return None
    
    try:
        from tts_provider import TTSRequest
        lang_code = "es" if language.startswith("es") else "en"
        req = TTSRequest(
            text=text,
            language=lang_code,
            output_format="mp3",
            output_path=output_path
        )
        result = client.generate_speech(req)
        if result.success:
            return {
                "path": result.audio_path,
                "size": result.bytes_generated,
                "provider": result.provider
            }
    except Exception as e:
        print(f"   ⚠️  TTS call failed: {e}")
    return None


def _generate_section_with_llm(
    section_title: str,
    language: str,
    context: str,
    client
) -> str:
    """Generate section content using OpenRouter LLM"""
    
    # System prompt based on language
    if language.startswith("es"):
        system_prompt = (
            "Eres un experto educativo en autoaprendizaje con IA. "
            "Escribe contenido educativo en español (LATAM). "
            "Tono profesional pero accesible, como una instrutora female latina."
        )

        prompt = (
            f'Escribe una sección completa sobre: "{section_title}"\n\n'
            f'Contexto: {context}\n\n'
            f'Requisitos:\n'
            f'- Extensión: ~400-500 palabras\n'
            f'- Formato Markdown con headers\n'
            f'- Incluir ejemplos prácticos\n'
            f'- Incluir ejercicios al final\n'
            f'- Tono: Educativo, motivador, profesional\n'
            f'- Idioma: Español LATAM'
        )
    
    else:  # English
        system_prompt = (
            "You are an expert educator in AI self-education. "
            "Write educational content in British English. "
            "Professional but accessible tone, like a female UK instructor."
        )

        prompt = (
            f'Write a complete section about: "{section_title}"\n\n'
            f'Context: {context}\n\n'
            f'Requirements:\n'
            f'- Length: ~400-500 words\n'
            f'- Format: Markdown with headers\n'
            f'- Include practical examples\n'
            f'- Include exercises at the end\n'
            f'- Tone: Educational, motivating, professional\n'
            f'- Language: British English'
        )

    content = _call_llm_generate(
        client, prompt, "anthropic/claude-3-haiku", language, system_prompt
    )
    
    if content:
        return content
    
    # Fallback template
    return f"# {section_title}\n\n[Content generated with LLM]\n\n## Key Points\n- {context}\n"


def _generate_full_content_with_llm(
    outline: Dict[str, Any],
    language: str,
    client
) -> Dict[str, Any]:
    """Generate full content from outline using LLM"""
    
    lang_name = "es-LATAM" if language.startswith("es") else "en-UK"
    
    content = {
        "language": lang_name,
        "title": outline["title"],
        "author": outline["author"],
        "description": outline["description"],
        "estimated_reading_time": outline["estimated_reading_time"],
        "sections": [],
        "word_count": 0,
        "generated_date": "2026-08-21"
    }
    
    # Build context
    context_parts = [
        f"Title: {outline['title']}",
        f"Description: {outline['description']}",
        f"Key points: {', '.join(outline.get('key_points', []))}",
    ]
    context = "\n".join(context_parts)
    
    for section in outline["sections"]:
        print(f"   📝 Generating section: {section['title'][:40]}...")
        
        section_content = _generate_section_with_llm(
            section["title"],
            language,
            context,
            client
        )
        
        section_data = {
            "title": section["title"],
            "content": section_content,
            "examples": section.get("examples", []),
            "exercises": section.get("exercises", []),
            "key_points": section.get("key_points", []),
            "estimated_time": section.get("estimated_time", 15),
            "resources": section.get("resources", [])
        }
        
        content["sections"].append(section_data)
        
        # Word count estimate
        words = len(section_content.split())
        content["word_count"] += words
        print(f"      ✅ {words} words")
    
    return content


def _generate_audio_for_sections(
    content: Dict[str, Any],
    language: str,
    output_dir: str = "outputs/audio"
) -> Dict[str, Any]:
    """Generate audio files for sections using TTS"""
    
    if HAS_TTS:
        try:
            import tts_provider as _tts_module
            client = _tts_module.TTSProviderClient()
        except Exception as e:
            print(f"   ⚠️  TTS client creation failed: {e}")
            return {"success": False, "error": str(e)}
    audio_files = []
    
    lang_code = "es" if language.startswith("es") else "en"
    
    for i, section in enumerate(content.get("sections", [])):
        print(f"   🔊 Audio section {i+1}: {section['title'][:40]}...")
        
        text = section.get("content", "")
        if not text:
            continue
        
        # Truncate for TTS
        max_chars = 3000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        output_path = f"{output_dir}/{language}_section_{i+1}.mp3"
        
        result = _call_tts_generate(client, text, language, output_path)
        
        if result:
            audio_files.append({
                "section": i + 1,
                "title": section["title"],
                "file": result["path"],
                "size": result["size"],
                "provider": result["provider"]
            })
            print(f"      ✅ Saved: {result['path']} ({result['size']} bytes)")
        else:
            print(f"      ⚠️  Failed")
    
    return {
        "success": True,
        "audio_files": audio_files,
        "total_size": sum(f["size"] for f in audio_files)
    }


def create_bilingual_outline(content: Dict[str, Any]) -> Dict[str, Any]:
    """Create bilingual outline from extracted content"""
    
    # Spanish version (LATAM Female tone)
    spanish_outline = {
        "title": f"Cómo auto educarse con IA. Método {content.get('title', 'Dan Martell')}",
        "language": "es-LATAM",
        "author": "Equipo AIIA-NTBLM-Factory",
        "description": "Guía completa de autoaprendizaje con IA siguiendo el método de Dan Martell",
        "estimated_reading_time": 90,
        "sections": [
            {
                "id": "intro",
                "title": "Introducción al Autoaprendizaje con IA",
                "key_points": content.get("key_points", [])[:2],
                "examples": [{"title": "Dan Martell - How to learn AI in 2025", "url": "https://www.youtube.com/watch?v=8G00aT2m4oU"}],
                "estimated_time": 15,
            },
            {
                "id": "basics",
                "title": "Conceptos Fundamentales",
                "key_points": content.get("key_points", [])[2:4],
                "examples": [{"title": "The Dan Martell Framework for Learning", "url": "https://danmartell.com/articles/self-education-ai"}],
                "estimated_time": 30,
            },
            {
                "id": "practice",
                "title": "Aplicación Práctica",
                "key_points": content.get("key_points", [])[4:6],
                "examples": [{"title": "Cómo aprender IA por ti mismo", "url": "https://www.youtube.com/watch?v=example-es"}],
                "estimated_time": 45,
            }
        ],
        "resources": [
            {"title": "Dan Martell - Official Channel", "url": "https://www.youtube.com/@DanMartell", "type": "youtube"},
            {"title": "Dan Martell Articles", "url": "https://danmartell.com/articles", "type": "website"}
        ]
    }
    
    # English version (UK Female tone)
    english_outline = {
        "title": f"How to self-educate with AI. {content.get('title', 'Dan Martell')} method",
        "language": "en-UK",
        "author": "AIIA-NTBLM-Factory Team",
        "description": "Complete guide to AI self-education following Dan Martell's methodology",
        "estimated_reading_time": 90,
        "sections": [
            {
                "id": "intro",
                "title": "Introduction to Self-Education with AI",
                "key_points": content.get("key_points", [])[:2],
                "examples": [{"title": "Dan Martell - How to learn AI in 2025", "url": "https://www.youtube.com/watch?v=8G00aT2m4oU"}],
                "estimated_time": 15,
            },
            {
                "id": "basics",
                "title": "Fundamental Concepts",
                "key_points": content.get("key_points", [])[2:4],
                "examples": [{"title": "The Dan Martell Framework for Learning", "url": "https://danmartell.com/articles/self-education-ai"}],
                "estimated_time": 30,
            },
            {
                "id": "practice",
                "title": "Practical Application",
                "key_points": content.get("key_points", [])[4:6],
                "examples": [{"title": "Cómo aprender IA por ti mismo", "url": "https://www.youtube.com/watch?v=example-es"}],
                "estimated_time": 45,
            }
        ],
        "resources": [
            {"title": "Dan Martell - Official Channel", "url": "https://www.youtube.com/@DanMartell", "type": "youtube"},
            {"title": "Dan Martell Articles", "url": "https://danmartell.com/articles", "type": "website"}
        ]
    }
    
    return {"spanish": spanish_outline, "english": english_outline}


def generate_content_from_outline(outline: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Generate full content from outline (template version)"""
    
    content = {
        "language": language,
        "title": outline["title"],
        "author": outline["author"],
        "description": outline["description"],
        "estimated_reading_time": outline["estimated_reading_time"],
        "sections": [],
        "word_count": 0,
        "generated_date": "2026-08-21"
    }
    
    for section in outline["sections"]:
        section_content = {
            "title": section["title"],
            "introduction": f"This section covers {section['title'].lower()}.",
            "content": f"# {section['title']}\n\n[Content to be generated with LLM]\n",
            "examples": section["examples"],
            "exercises": [
                "Practice activity 1",
                "Case study analysis",
                "Implementation project"
            ],
            "key_points": section["key_points"],
            "estimated_time": section["estimated_time"],
            "resources": section.get("resources", [])
        }
        
        content["sections"].append(section_content)
        content["word_count"] += 500  # Placeholder
    
    return content


print(f"✅ Part 3 loaded: Content generation (LLM={HAS_LLM}, TTS={HAS_TTS})")