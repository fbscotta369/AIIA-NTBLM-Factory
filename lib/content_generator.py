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
        "voice_id": "XbQXCjpM9k00zzSX8vD7",
        "language": "es",
        "stability": 0.4,
        "similarity_boost": 0.75,
    },
    "en": {
        "name": "English (British) - Female",
        "voice_id": "Thq69S6I3X0H6kVrBU9P",
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
    """Generate markdown documentation from NotebookLM analysis."""
    topic = analysis.get("topic", "Documento generado por AIIA-NTBLM-Factory")
    lang_name = LANG_NAMES.get(lang, lang)

    summary = analysis.get("summary", [])
    slides = analysis.get("slides", [])
    faq = analysis.get("faq", [])
    timeline = analysis.get("timeline", [])
    insights = analysis.get("insights", [])

    md = f"""# {topic}

**Generado por AIIA-NTBLM-Factory v1.0**
*Idioma: {lang_name} | Voz: Femenina*

---

## Introduccion

"""
    if summary:
        md += "### Resumen\n\n"
        for line in summary[:20]:
            md += f"{line}\n\n"

    md += """---

## Contenido Principal

"""
    if insights:
        md += "### Ideas Clave / Key Insights\n\n"
        for insight in insights[:10]:
            md += f"- {insight}\n"
        md += "\n"

    if slides:
        md += "### Diapositivas / Slides\n\n"
        for slide in slides[:10]:
            md += f"> {slide}\n\n"

    md += """---

## Preguntas Frecuentes / FAQ

"""
    if faq:
        for q in faq[:10]:
            md += f"**Q:** {q}\n\n"

    md += """---

## Linea de Tiempo / Timeline

"""
    if timeline:
        for event in timeline[:10]:
            md += f"- {event}\n"

    md += f"""
---

## Conclusión

Este documento fue generado automaticamente por AIIA-NTBLM-Factory v1.0 utilizando NotebookLM para el analisis profundo de las fuentes proporcionadas.

**Idioma:** {lang_name}
**Fecha de generación:** {datetime.now().strftime("%Y-%m-%d")}
**Version:** 1.0

---

## Apéndice / Appendix

### Fuentes
- YouTube videos procesados a traves de NotebookLM

### Glosario
- *NotebookLM*: Herramienta de Google para analisis de documentos con IA
- *AIIA-NTBLM-Factory*: Fabrica de productos digitales impulsada por NotebookLM

---

*Documento generado automaticamente — AIIA-NTBLM-Factory v1.0*
"""
    return md


def generate_slides(analysis: Dict, lang: str = "es") -> List[Dict]:
    """Generate slide data from NotebookLM analysis."""
    slides = []
    topic = analysis.get("topic", "Presentacion")
    slides.append({"title": topic, "content": ["AIIA-NTBLM-Factory v1.0"], "visual": None})

    summary = analysis.get("summary", [])
    if summary:
        slides.append({"title": "Introduccion / Introduction", "content": summary[:5], "visual": None})

    insights = analysis.get("insights", [])
    for i, insight in enumerate(insights[:8]):
        slides.append({"title": f"Insight {i+1}", "content": [insight], "visual": None})

    faq = analysis.get("faq", [])
    if faq:
        slides.append({"title": "Preguntas Frecuentes / FAQ", "content": faq[:5], "visual": None})

    timeline = analysis.get("timeline", [])
    if timeline:
        slides.append({"title": "Linea de Tiempo / Timeline", "content": timeline[:8], "visual": None})

    return slides


def generate_infographics(analysis: Dict, lang: str = "es") -> List[Dict]:
    """Generate infographic SVG data from NotebookLM analysis."""
    infographics = []

    timeline = analysis.get("timeline", [])
    if timeline:
        svg_lines = [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">',
            '  <style>',
            '    .title { font: bold 24px Arial; fill: #1a1a2e; }',
            '    .event { font: 14px Arial; fill: #333; }',
            '    .line { stroke: #4a90d9; stroke-width: 3; fill: none; }',
            '    .dot { fill: #4a90d9; }',
            '  </style>',
            '  <text x="400" y="40" text-anchor="middle" class="title">Timeline</text>',
            '  <line x1="50" y1="100" x2="750" y2="100" class="line"/>',
        ]
        for i, event in enumerate(timeline[:8]):
            x = 50 + (i * 100)
            svg_lines.append('  <circle cx="{}" cy="100" r="8" class="dot"/>'.format(x))
            svg_lines.append('  <text x="{}" y="130" text-anchor="middle" class="event">{}</text>'.format(x, event[:50]))
        svg_lines.append("</svg>")
        infographics.append({"title": "Timeline", "svg": "\n".join(svg_lines), "filename": "timeline.svg"})

    insights = analysis.get("insights", [])
    if insights:
        nodes = insights[:6]
        svg_lines = [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">',
            '  <style>',
            '    .concept { font: 14px Arial; fill: #1a1a2e; }',
            '    .center { font: bold 18px Arial; fill: #fff; }',
            '    .box { fill: #4a90d9; }',
            '  </style>',
            '  <text x="400" y="40" text-anchor="middle" class="center">Concept Map</text>',
        ]
        for i, concept in enumerate(nodes):
            col = i % 3
            row = i // 3
            x = 50 + col * 250
            y = 80 + row * 150
            svg_lines.append('  <rect x="{}" y="{}" width="220" height="80" rx="8" class="box" opacity="0.2"/>'.format(x, y))
            svg_lines.append('  <text x="{}" y="{}" class="concept">{}. {}:</text>'.format(x + 10, y + 25, i + 1, concept[:60]))
        svg_lines.append("</svg>")
        infographics.append({"title": "Concept Map", "svg": "\n".join(svg_lines), "filename": "concepts.svg"})

    return infographics


def generate_audio(text: str, lang: str = "es", voice: str = "female") -> Dict:
    """Generate audio narration from text using ElevenLabs TTS."""
    if not ELEVENLABS_AVAILABLE:
        return {"path": None, "duration": 0, "voice": VOICE_CONFIGS.get(lang, {}).get("name", ""), "error": "elevenlabs library not installed"}

    if not ELEVENLABS_API_KEY:
        return {"path": None, "duration": 0, "voice": VOICE_CONFIGS.get(lang, {}).get("name", ""), "error": "ELEVENLABS_API_KEY not set"}

    voice_config = VOICE_CONFIGS.get(lang, VOICE_CONFIGS["en"])

    try:
        client = elevenlabs.ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.generate(
            text=text,
            voice=voice_config["voice_id"],
            model="eleven_multilingual_v2",
            voice_settings={"stability": voice_config.get("stability", 0.4), "similarity_boost": voice_config.get("similarity_boost", 0.75)},
        )

        lang_dir = ROOT / "output" / "audio"
        lang_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        filepath = lang_dir / filename

        with open(filepath, "wb") as f:
            f.write(audio)

        duration = get_audio_duration(filepath)
        print(f"  Audio generado: {filepath} ({duration:.1f}s)")
        return {"path": str(filepath), "duration": duration, "voice": voice_config["name"], "voice_id": voice_config["voice_id"]}
    except Exception as e:
        print(f"  Error generando audio: {e}")
        return {"path": None, "duration": 0, "voice": voice_config.get("name", ""), "error": str(e)}


def generate_video(slides: List[Dict], audio: Optional[Dict], lang: str = "es") -> Dict:
    """Generate video from slides + audio using FFmpeg."""
    if not audio or not audio.get("path"):
        return {"path": None, "duration": 0, "error": "No audio provided for video generation"}

    audio_path = Path(audio["path"])
    if not audio_path.exists():
        return {"path": None, "duration": 0, "error": f"Audio file not found: {audio_path}"}

    audio_duration = audio.get("duration", 0)
    if audio_duration == 0:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
                capture_output=True, text=True,
            )
            audio_duration = float(result.stdout.strip())
        except Exception:
            audio_duration = 30

    num_slides = len(slides) if slides else 1
    slide_duration = audio_duration / num_slides

    temp_dir = Path(tempfile.mkdtemp(prefix="aiia_video_"))

    try:
        for i, slide in enumerate(slides):
            generate_slide_image(slide, temp_dir / f"slide_{i:03d}.png")

        concat_file = temp_dir / "concat.txt"
        with open(concat_file, "w") as f:
            for i in range(num_slides):
                f.write(f"file '{temp_dir / f'slide_{i:03d}.png'}.resolve()'\\n")
                f.write(f"duration {slide_duration:.3f}\\n")
            f.write(f"file '{temp_dir / f'slide_{num_slides-1:03d}.png'}.resolve()'\\n")

        output_path = ROOT / "output" / "video" / f"{lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file), "-i", str(audio_path),
            "-c:v", "libx264", "-c:a", "aac", "-shortest",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-r", "30", "-movflags", "+faststart",
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return {"path": None, "duration": 0, "error": f"FFmpeg failed: {result.stderr[:200]}"}

        output_duration = get_video_duration(output_path)
        print(f"  Video generado: {output_path} ({output_duration:.1f}s)")
        return {"path": str(output_path), "duration": output_duration, "slides_count": num_slides}

    except Exception as e:
        print(f"  Error generando video: {e}")
        return {"path": None, "duration": 0, "error": str(e)}
    finally:
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


def generate_quiz(analysis: Dict, lang: str = "es") -> Dict:
    """Generate quiz questions from NotebookLM analysis."""
    questions = []
    insights = analysis.get("insights", [])
    faq = analysis.get("faq", [])

    if insights:
        for i, insight in enumerate(insights[:5]):
            questions.append({
                "type": "multiple_choice",
                "question": insight[:100],
                "options": [
                    f"Opcion A: {insight[:80]}",
                    f"Opcion B: Variacion de {insight[:60]}",
                    f"Opcion C: Contraste con {insight[:60]}",
                    f"Opcion D: Extension de {insight[:60]}",
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
                "explanation": "Esta pregunta esta basada en el contenido del FAQ del documento.",
            })

    return {"questions": questions, "total": len(questions), "language": lang, "generated_at": datetime.now().isoformat()}


# =============================================================================
# Internal helpers
# =============================================================================

def get_audio_duration(filepath: Path) -> float:
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
    """Generate a slide image using matplotlib (preferred) or PIL fallback."""
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(16, 9), facecolor="#1a1a2e")
        ax.set_facecolor("#1a1a2e")
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 9)
        ax.axis("off")

        ax.text(8, 8.2, slide.get("title", "Sin titulo"), ha="center", va="center",
                fontsize=24, color="#4a90d9", fontweight="bold")

        content_lines = slide.get("content", [])
        y_pos = 6.5
        for line in content_lines[:8]:
            ax.text(1, y_pos, "• " + line[:100], ha="left", va="top", fontsize=14, color="#e0e0e0")
            y_pos -= 0.5

        ax.text(15, 0.3, "AIIA-NTBLM-Factory v1.0", ha="right", va="center", fontsize=10, color="#666")

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()

    except ImportError:
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

        draw.text((100, 80), slide.get("title", "Sin titulo"), fill="#4a90d9", font=font_large)

        content_lines = slide.get("content", [])
        y = 200
        for line in content_lines[:10]:
            draw.text((100, y), "• " + line[:100], fill="#e0e0e0", font=font_medium)
            y += 40

        draw.text((1820, 1040), "AIIA-NTBLM-Factory v1.0", fill="#666", font=font_small, anchor="ra")

        img.save(output_path)


if __name__ == "__main__":
    print("=== Content Generator Test ===")
    print(f"  ElevenLabs available: {ELEVENLABS_AVAILABLE}")
    print(f"  ELEVENLABS_API_KEY set: {bool(ELEVENLABS_API_KEY)}")

    test_analysis = {
        "topic": "Test de generacion de contenido",
        "summary": ["Este es un resumen de prueba.", "Contiene informacion importante."],
        "insights": ["Primer insight importante.", "Segundo insight clave."],
        "slides": ["Diapositiva 1", "Diapositiva 2"],
        "faq": ["Que es esto?", "Como funciona?"],
        "timeline": ["Evento 1", "Evento 2", "Evento 3"],
    }

    for lang in ["es", "en"]:
        print(f"\n  Documento en {LANG_NAMES[lang]}:")
        docs = generate_docs(test_analysis, lang=lang)
        print(f"    Longitud: {len(docs)} chars")
        print(f"    Primeras 200 chars:\n    {docs[:200]}...")

    print(f"\n  Diapositivas para 'es':")
    slides = generate_slides(test_analysis, lang="es")
    print(f"    Total: {len(slides)} diapositivas")
    for s in slides[:3]:
        print(f"    - {s['title']}")

    print(f"\n  Infografias para 'es':")
    infographics = generate_infographics(test_analysis, lang="es")
    print(f"    Total: {len(infographics)} infografias")
    for inf in infographics:
        print(f"    - {inf['title']} ({len(inf['svg'])} bytes SVG)")

    print(f"\n  Generacion de audio (demo sin API key):")
    result = generate_audio("Texto de prueba para narracion.", lang="es", voice="female")
    print(f"    Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
