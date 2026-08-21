#!/usr/bin/env python3
"""
AIIA-NTBLM-Factory — Content Generator
Takes NotebookLM analysis and generates:
- Markdown docs (bilingual)
- Slides (SVG/Mermaid)
- Infographics (SVG)
- Audio (via ElevenLabs TTS)
- Video (via FFmpeg)
- Quiz (questions + answers)

All generated in 2 languages: ES (LatAm, female voice) + EN (British, female voice)
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# ElevenLabs TTS
try:
    import elevenlabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

# Config
ROOT = Path(__file__).parent.parent.resolve()
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Voice configurations
VOICE_CONFIGS = {
    "es": {
        "name": "Spanish (Latin American) - Female",
        "voice_id": "XbQXCjpM9k00zzSX8vD7",  # María (LatAm)
        "language": "es",
        "stability": 0.4,
        "similarity_boost": 0.75,
    },
    "en": {
        "name": "English (British) - Female",
        "voice_id": "Thq69S6I3X0H6kVrBU9P",  # Alice (British)
        "language": "en",
        "stability": 0.4,
        "similarity_boost": 0.75,
    },
}

LANG_NAMES = {
    "es": "Español (Latinoamericano)",
    "en": "English (British)",
}


def generate_docs(analysis: Dict, lang: str = "es") -> str:
    """
    Generate markdown documentation from NotebookLM analysis.

    Structure:
    - Cover page (title, subtitle, author, date)
    - Table of contents
    - Introduction
    - Main content (from summary + slides + insights)
    - Key takeaways
    - FAQ
    - Timeline
    - Conclusion
    - Appendix (sources, glossary)
    """
    # Generate title from topic (if available) or default
    topic = analysis.get("topic", "Documento generado por AIIA-NTBLM-Factory")
    lang_name = LANG_NAMES.get(lang, lang)

    # Build content sections
    summary = analysis.get("summary", [])
    slides = analysis.get("slides", [])
    faq = analysis.get("faq", [])
    timeline = analysis.get("timeline", [])
    insights = analysis.get("insights", [])

    # Build markdown
    md = f"""# {topic}

**Generado por AIIA-NTBLM-Factory v1.0**
*Idioma: {lang_name} | Voz: Femenina*

---

## Introducción

"""

    # Add summary content
    if summary:
        md += "### Resumen\n\n"
        for line in summary[:20]:  # first 20 lines of summary
            md += f"{line}\n\n"

    md += f"""---

## Contenido Principal

"""

    # Add insights as main content
    if insights:
        md += "### Ideas Clave / Key Insights\n\n"
        for insight in insights[:10]:
            md += f"- {insight}\n"
        md += "\n"

    # Add slides content
    if slides:
        md += "### Diapositivas / Slides\n\n"
        for slide in slides[:10]:
            md += f"> {slide}\n\n"

    md += f"""---

## Preguntas Frecuentes / FAQ

"""

    if faq:
        for q in faq[:10]:
            md += f"**Q:** {q}\n\n"

    md += f"""---

## Línea de Tiempo / Timeline

"""

    if timeline:
        for event in timeline[:10]:
            md += f"- {event}\n"

    md += f"""
---

## Conclusión

Este documento fue generado automáticamente por AIIA-NTBLM-Factory v1.0 utilizando PocketBookLM para el análisis profundo de las fuentes proporcionadas.

**Idioma:** {lang_name}
**Fecha de generación:** {datetime.now().strftime("%Y-%m-%d")}
**Versión:** 1.0

---

## Apéndice / Appendix

### Fuentes
- YouTube videos processed through NotebookLM

### Glosario
- *NotebookLM*: Herramienta de Google para análisis de documentos con IA
- *AIIA-NTBLM-Factory*: Fábrica de productos digitales impulsada por NotebookLM

---

*Documento generado automáticamente — AIIA-NTBLM-Factory v1.0*
"""

    return md


def generate_slides(analysis: Dict, lang: str = "es") -> List[Dict]:
    """
    Generate slide data from NotebookLM analysis.

    Returns list of slide dicts with:
        - title: slide title
        - content: bullet points or text
        - visual: SVG/mermaid diagram reference (optional)
    """
    slides = []

    # Slide 1: Title slide
    topic = analysis.get("topic", "Presentación")
    slides.append({
        "title": topic,
        "content": ["AIIA-NTBLM-Factory v1.0"],
        "visual": None,
    })

    # Slide 2: Introduction
    summary = analysis.get("summary", [])
    if summary:
        slides.append({
            "title": "Introducción / Introduction",
            "content": summary[:5],
            "visual": None,
        })

    # Slide 3+: Key insights
    insights = analysis.get("insights", [])
    for i, insight in enumerate(insights[:8]):
        slides.append({
            "title": f"Insight {i+1}",
            "content": [insight],
            "visual": None,
        })

    # FAQ slide
    faq = analysis.get("faq", [])
    if faq:
        slides.append({
            "title": "Preguntas Frecuentes / FAQ",
            "content": faq[:5],
            "visual": None,
        })

    # Timeline slide
    timeline = analysis.get("timeline", [])
    if timeline:
        slides.append({
            "title": "Línea de Tiempo / Timeline",
            "content": timeline[:8],
            "visual": None,
        })

    return slides


def generate_infographics(analysis: Dict, lang: str = "es") -> List[Dict]:
    """
    Generate infographic SVG data from NotebookLM analysis.

    Creates visual representations like:
    - Concept maps
    - Timeline visualizations
    - Process diagrams
    """
    infographics = []

    # 1. Timeline infographic
    timeline = analysis.get("timeline", [])
    if timeline:
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
  <style>
    .title { font: bold 24px Arial; fill: #1a1a2e; }
    .event { font: 14px Arial; fill: #333; }
    .line { stroke: #4a90d9; stroke-width: 3; fill: none; }
    .dot { fill: #4a90d9; }
    .label { font: 12px Arial; fill: #666; }
  </style>
  <text x="400" y="40" text-anchor="middle" class="title">Línea de Tiempo / Timeline</text>
  <line x1="50" y1="100" x2="750" y2="100" class="line"/>
"""
        for i, event in enumerate(timeline[:8]):
            x = 50 + (i * 100)
            svg_content += f"""
  <circle cx="{x}" cy="100" r="8" class="dot"/>
  <text x="{x}" y="130" text-anchor="middle" class="event">{event[:50]}</text>
"""

        svg_content += "</svg>"
        infographics.append({
            "title": "Timeline",
            "svg": svg_content,
            "filename": "timeline.svg",
        })

    # 2. Key concepts diagram (concept map)
    insights = analysis.get("insights", [])
    if insights:
        nodes = insights[:6]
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <style>
    .concept { font: 14px Arial; fill: #1a1a2e; }
    .center { font: bold 18px Arial; fill: #fff; }
    .arrow { stroke: #4a90d9; stroke-width: 2; fill: none; marker-end: url(#arrow); }
    .box { fill: #4a90d9; }
  </style>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#4a90d9"/>
    </marker>
  </defs>
  <text x="400" y="40" text-anchor="middle" class="center">Conceptos Clave / Key Concepts</text>
"""
        # Create a simple grid of concept boxes
        cols = 3
        for i, concept in enumerate(nodes):
            col = i % cols
            row = i // cols
            x = 50 + col * 250
            y = 80 + row * 150

            svg_content += f"""
  <rect x="{x}" y="{y}" width="220" height="80" rx="8" class="box" opacity="0.2"/>
  <text x="{x+10}" y="{y+25}" class="concept">{i+1}. {concept[:60]}</text>
"""

        svg_content += "</svg>"
        infographics.append({
            "title": "Conceptos Clave / Key Concepts",
            "svg": svg_content,
            "filename": "concepts.svg",
        })

    return infographics


def generate_audio(text: str, lang: str = "es", voice: str = "female") -> Dict:
    """
    Generate audio narration from text using ElevenLabs TTS.

    Returns dict with:
        - path: path to generated MP3 file
        - duration: duration in seconds
        - voice: voice used
    """
    if not ELEVENLABS_AVAILABLE:
        return {
            "path": None,
            "duration": 0,
            "voice": VOICE_CONFIGS.get(lang, {}).get("name", ""),
            "error": "elevenlabs library not installed",
        }

    if not ELEVENLABS_API_KEY:
        return {
            "path": None,
            "duration": 0,
            "voice": VOICE_CONFIGS.get(lang, {}).get("name", ""),
            "error": "ELEVENLABS_API_KEY not set",
        }

    voice_config = VOICE_CONFIGS.get(lang, VOICE_CONFIGS["en"])

    try:
        client = elevenlabs.ElevenLabs(api_key=ELEVENLABS_API_KEY)

        # Generate audio
        audio = client.generate(
            text=text,
            voice=voice_config["voice_id"],
            model="eleven_multilingual_v2",
            voice_settings={
                "stability": voice_config.get("stability", 0.4),
                "similarity_boost": voice_config.get("similarity_boost", 0.75),
            },
        )

        # Save to file
        lang_dir = ROOT / "output" / "audio"
        lang_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        filepath = lang_dir / filename

        with open(filepath, "wb") as f:
            f.write(audio)

        # Get duration using ffprobe
        duration = get_audio_duration(filepath)

        print(f"  🔊 Audio generado: {filepath} ({duration:.1f}s)")

        return {
            "path": str(filepath),
            "duration": duration,
            "voice": voice_config["name"],
            "voice_id": voice_config["voice_id"],
        }

    except Exception as e:
        print(f"  ❌ Error generating audio: {e}")
        return {
            "path": None,
            "duration": 0,
            "voice": voice_config.get("name", ""),
            "error": str(e),
        }


def generate_video(slides: List[Dict], audio: Optional[Dict], lang: str = "es") -> Dict:
    """
    Generate video from slides + audio using FFmpeg.

    Creates a slide-show video where each slide is displayed for a portion
    of the audio duration.

    Returns dict with:
        - path: path to generated MP4 file
        - duration: duration in seconds
    """
    if not audio or not audio.get("path"):
        return {
            "path": None,
            "duration": 0,
            "error": "No audio provided for video generation",
        }

    audio_path = Path(audio["path"])
    if not audio_path.exists():
        return {
            "path": None,
            "duration": 0,
            "error": f"Audio file not found: {audio_path}",
        }

    # Get audio duration
    audio_duration = audio.get("duration", 0)
    if audio_duration == 0:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
                capture_output=True, text=True,
            )
            audio_duration = float(result.stdout.strip())
        except Exception:
            audio_duration = 30  # fallback

    # Calculate slide duration (equal time per slide)
    num_slides = len(slides) if slides else 1
    slide_duration = audio_duration / num_slides

    # Create temp directory for slides
    temp_dir = Path(tempfile.mkdtemp(prefix="aiia_video_"))

    try:
        # Generate slide images
        for i, slide in enumerate(slides):
            slide_img = temp_dir / f"slide_{i:03d}.png"
            generate_slide_image(slide, slide_img)

        # Create FFmpeg command to concatenate slides with audio
        # Use concat demuxer with slide durations
        concat_file = temp_dir / "concat.txt"
        with open(concat_file, "w") as f:
            for i in range(num_slides):
                slide_img = temp_dir / f"slide_{i:03d}.png"
                f.write(f"file '{slide_img.resolve()}'\n")
                f.write(f"duration {slide_duration:.3f}\n")

        # Add last slide without duration (holds until audio ends)
        last_slide = temp_dir / f"slide_{num_slides-1:03d}.png"
        concat_file.write(f"file '{last_slide.resolve()}'\n")

        output_path = ROOT / "output" / "video" / f"{lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Run FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-r", "30",
            "-movflags", "+faststart",
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"  ❌ FFmpeg error: {result.stderr[:500]}")
            return {
                "path": None,
                "duration": 0,
                "error": f"FFmpeg failed: {result.stderr[:200]}",
            }

        # Get output duration
        output_duration = get_video_duration(output_path)

        print(f"  🎬 Video generado: {output_path} ({output_duration:.1f}s)")

        return {
            "path": str(output_path),
            "duration": output_duration,
            "slides_count": num_slides,
        }

    except Exception as e:
        print(f"  ❌ Error generating video: {e}")
        return {
            "path": None,
            "duration": 0,
            "error": str(e),
        }
    finally:
        # Cleanup temp dir
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


def generate_quiz(analysis: Dict, lang: str = "es") -> Dict:
    """
    Generate quiz questions from NotebookLM analysis.

    Returns dict with:
        - questions: list of question dicts with question, options, answer, explanation
        - total: number of questions
    """
    questions = []

    # Generate questions based on available content
    summary = analysis.get("summary", [])
    insights = analysis.get("insights", [])
    faq = analysis.get("faq", [])

    # Question templates
    if insights:
        for i, insight in enumerate(insights[:5]):
            questions.append({
                "type": "multiple_choice",
                "question": insight[:100],
                "options": [
                    f"Opción A: {insight[:80]}",
                    f"Opción B: Variación de {insight[:60]}",
                    f"Opción C: Contraste con {insight[:60]}",
                    f"Opción D: Extensión de {insight[:60]}",
                ],
                "answer": 0,
                "explanation": f"La respuesta correcta se basa en el insight: {insight[:100]}",
            })

    if faq:
        for i, question_text in enumerate(faq[:5]):
            questions.append({
                "type": "open_ended",
                "question": question_text[:100],
                "answer": "Ver resumen del documento para la respuesta detallada.",
                "explanation": f"Esta pregunta está basada en el contenido del FAQ del documento.",
            })

    return {
        "questions": questions,
        "total": len(questions),
        "language": lang,
        "generated_at": datetime.now().isoformat(),
    }


# =============================================================================
# Internal helpers
# =============================================================================

def get_audio_duration(filepath: Path) -> float:
    """Get audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def get_video_duration(filepath: Path) -> float:
    """Get video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def generate_slide_image(slide: Dict, output_path: Path):
    """Generate a slide image using matplotlib (placeholder)."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        fig, ax = plt.subplots(figsize=(16, 9), facecolor="#1a1a2e")
        ax.set_facecolor("#1a1a2e")
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 9)
        ax.axis("off")

        # Title
        title_color = "#4a90d9"
        ax.text(8, 8.2, slide.get("title", "Sin título"),
                ha="center", va="center", fontsize=24, color=title_color, fontweight="bold")

        # Content
        content_lines = slide.get("content", [])
        content_color = "#e0e0e0"
        y_pos = 6.5
        for line in content_lines[:8]:
            ax.text(1, y_pos, f"• {line[:100]}",
                    ha="left", va="top", fontsize=14, color=content_color)
            y_pos -= 0.5

        # Footer
        ax.text(15, 0.3, "AIIA-NTBLM-Factory v1.0", ha="right", va="center",
                fontsize=10, color="#666")

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()

    except ImportError:
        # Fallback: create a simple colored image with PIL
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (1920, 1080), color="#1a1a2e")
        draw = ImageDraw.Draw(img)

        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except Exception:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Title
        title = slide.get("title", "Sin título")
        draw.text((100, 80), title, fill="#4a90d9", font=font_large)

        # Content
        content_lines = slide.get("content", [])
        y = 200
        for line in content_lines[:10]:
            draw.text((100, y), f"• {line[:100]}", fill="#e0e0e0", font=font_medium)
            y += 40

        # Footer
        draw.text((1820, 1040), "AIIA-NTBLM-Factory v1.0", fill="#666", font=font_small, anchor="ra")

        img.save(output_path)

    return output_path


if __name__ == "__main__":
    # Quick test
    print("=== Content Generator Test ===")
    print(f"  ElevenLabs available: {ELEVENLABS_AVAILABLE}")
    print(f"  ELEVENLABS_API_KEY set: {bool(ELEVENLABS_API_KEY)}")

    # Test doc generation
    test_analysis = {
        "topic": "Test de generación de contenido",
        "summary": ["Este es un resumen de prueba.", "Contiene información importante."],
        "insights": ["Primer insight importante.", "Segundo insight clave."],
        "slides": ["Diapositiva 1", "Diapositiva 2"],
        "faq": ["¿Qué es esto?", "¿Cómo funciona?"],
        "timeline": ["Evento 1", "Evento 2", "Evento 3"],
    }

    # Generate docs in both languages
    for lang in ["es", "en"]:
        print(f"\n  📄 Documento en {LANG_NAMES[lang]}:")
        docs = generate_docs(test_analysis, lang=lang)
        print(f"    Longitud: {len(docs)} chars")
        print(f"    Primeras 200 chars:\n    {docs[:200]}...")

    # Generate slides
    print(f"\n  🖼️  Diapositivas para 'es':")
    slides = generate_slides(test_analysis, lang="es")
    print(f"    Total: {len(slides)} diapositivas")
    for s in slides[:3]:
        print(f"    - {s['title']}")

    # Generate infographics
    print(f"\n  📊 Infografías para 'es':")
    infographics = generate_infographics(test_analysis, lang="es")
    print(f"    Total: {len(infographics)} infografías")
    for inf in infographics:
        print(f"    - {inf['title']} ({len(inf['svg'])} bytes SVG)")

    # Test audio (will fail without API key, but shows structure)
    print(f"\n  🔊 Generación de audio (demo sin API key):")
    result = generate_audio("Texto de prueba para narración.", lang="es", voice="female")
    print(f"    Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
