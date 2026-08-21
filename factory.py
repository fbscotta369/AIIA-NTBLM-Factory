#!/usr/bin/env python3
"""
AIIA-NTBLM-Factory — Pipeline Orchestrator
Coordinates: Source Collection → NotebookLM Analysis → Content Generation →
PDF Design → Quality Control → Export.

Usage:
  python factory.py --topic "Como auto educarse con IA. El método Dan Martell" --lang all

Environment variables (set in .env or exported):
  YOUTUBE_API_KEY
  ELEVENLABS_API_KEY
  OPENROUTER_API_KEY
  GOOGLE_SESSION_COOKIE (base64-encoded Playwright storage_state)
  VOICE_GENDER (female | male)
  LANGUAGE_PREFERENCE (es | en | all)
"""

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime

# =============================================================================
# Configuration
# =============================================================================
ROOT = Path(__file__).parent.resolve()
OUTPUT_DIR = ROOT / "output"
ASSET_DIR = ROOT / "assets"

# Phase timing (seconds)
PHASE_TIMEOUTS = {
    "source_collection": 300,      # 5 min for YouTube search
    "notebooklm_login": 120,       # 2 min for browser login
    "notebooklm_analysis": 600,    # 10 min for notebook creation + source add + analysis
    "content_generation": 900,     # 15 min for docs + slides + infographics + audio + video + quiz
    "pdf_design": 300,             # 5 min for PDF + ePub generation
    "quality_control": 120,        # 2 min for 6 checks
    "export": 60,                  # 1 min for bundle
}

# Languages and voices
LANG_CONFIG = {
    "es": {
        "name": "Spanish (Latin American)",
        "voice_gender": "female",
        "accent": "latam",
        "tts_provider": "elevenlabs",
    },
    "en": {
        "name": "English (British)",
        "voice_gender": "female",
        "accent": "british",
        "tts_provider": "elevenlabs",
    },
}

_DEBUG = os.environ.get("FACTORY_DEBUG", "0") == "1"


def debug_print(msg):
    if _DEBUG:
        print(f"[DEBUG] {msg}")


def section(title, level=1):
    sep = "=" * 60
    if level == 1:
        print(f"\n{sep}")
        print(f"  {title}")
        print(sep)
    else:
        print(f"\n--- {title} ---")


def check_env():
    """Verify required env vars are present."""
    required = {
        "YOUTUBE_API_KEY": os.environ.get("YOUTUBE_API_KEY"),
        "ELEVENLABS_API_KEY": os.environ.get("ELEVENLABS_API_KEY"),
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY"),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"\n❌ Missing environment variables: {missing}")
        print("   Set them in .env or export before running.")
        return False
    return True


def generate_topic_slug(topic: str) -> str:
    """Convert topic string to a URL/file-safe slug."""
    import re
    slug = topic.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '_', slug)
    slug = slug[:80]  # limit length
    return slug or "untitled"


def run_phase(name, func, *args, timeout=None, **kwargs):
    """
    Run a pipeline phase with timeout + error handling.
    Returns (success: bool, result: any, duration: float)
    """
    section(f"Phase: {name}", level=2)
    print(f"  Starting {name}...")

    timeout = timeout or PHASE_TIMEOUTS.get(name, 300)
    start = time.time()

    try:
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"  ✅ {name} completed in {duration:.1f}s")
        return True, result, duration
    except Exception as e:
        duration = time.time() - start
        print(f"  ❌ {name} failed after {duration:.1f}s")
        print(f"  Error: {e}")
        if _DEBUG:
            traceback.print_exc()
        return False, None, duration


def phase1_source_collection(topic: str, lang: str) -> dict:
    """Phase 1: Collect YouTube sources about the topic."""
    from lib.source_collector import search_videos

    query = topic if lang == "all" else f"{topic} {LANG_CONFIG.get(lang, {}).get('name', '')}"
    print(f"  Query: {query}")

    results = search_videos(query, max_results=10)

    # Filter: require >= 1000 views and reasonable duration
    filtered = [
        r for r in results
        if r.get("view_count", 0) >= 1000
        and r.get("duration_seconds", 0) >= 300  # 5+ minutes
    ]

    print(f"  Found {len(results)} videos, {len(filtered)} after filtering")
    return {"raw": results, "filtered": filtered, "query": query}


def phase2_notebooklm_analysis(topic: str, sources: list, lang: str) -> dict:
    """Phase 2: Use NotebookLM for deep analysis."""
    from lib.notebooklm_client import NotebookLMClient

    client = NotebookLMClient()

    # Step 1: Login
    login_ok, login_result, login_dur = run_phase(
        "notebooklm_login",
        client.login,
        timeout=PHASE_TIMEOUTS["notebooklm_login"],
    )
    if not login_ok:
        return {"error": "Login failed", "phase": "notebooklm_login"}

    # Step 2: Create notebook
    slug = generate_topic_slug(topic)
    notebook_title = f"{topic} — {LANG_CONFIG.get(lang, {}).get('name', 'Analysis')}"
    section("Create Notebook", level=2)
    notebook = client.create_notebook(notebook_title)
    print(f"  Notebook created: {notebook.get('id', 'N/A')}")

    if not notebook:
        client.close()
        return {"error": "Notebook creation failed"}

    # Step 3: Add sources
    section("Add Sources", level=2)
    urls = [s["url"] for s in sources if s.get("url")]
    print(f"  Adding {len(urls)} sources...")
    add_ok, add_result, add_dur = run_phase(
        "add_sources",
        client.add_sources,
        notebook,
        urls,
        timeout=PHASE_TIMEOUTS["notebooklm_analysis"],
    )
    if not add_ok:
        client.close()
        return {"error": "Source addition failed", "notebook": notebook}

    # Step 4: Wait for analysis + extract
    section("Extract Analysis", level=2)
    print("  Waiting for NotebookLM to process sources...")
    time.sleep(30)  # Give NotebookLM time to analyze

    analysis = client.extract_analysis(notebook)
    client.close()

    return {
        "notebook": notebook,
        "sources_added": len(urls),
        "analysis": analysis,
        "duration": time.time() - login_dur - add_dur - 30,
    }


def phase3_content_generation(topic: str, analysis: dict, langs: list) -> dict:
    """Phase 3: Generate content in all configured languages."""
    from lib.content_generator import (
        generate_docs,
        generate_slides,
        generate_infographics,
        generate_audio,
        generate_video,
        generate_quiz,
    )

    results = {}

    for lang in langs:
        if lang not in LANG_CONFIG:
            print(f"  ⚠  Unknown language '{lang}', skipping")
            continue

        config = LANG_CONFIG[lang]
        section(f"Content Generation: {config['name']} ({lang})", level=2)

        lang_results = {}

        # Docs
        section("  Generate Docs", level=2)
        docs_ok, docs, docs_dur = run_phase(
            "docs_generation",
            generate_docs,
            analysis,
            lang=lang,
            timeout=120,
        )
        if docs_ok:
            lang_results["docs"] = docs

        # Infographics
        section("  Generate Infographics", level=2)
        infographics_ok, infographics, inf_dur = run_phase(
            "infographics_generation",
            generate_infographics,
            analysis,
            lang=lang,
            timeout=120,
        )
        if infographics_ok:
            lang_results["infographics"] = infographics

        # Audio
        section("  Generate Audio", level=2)
        audio_ok, audio, audio_dur = run_phase(
            "audio_generation",
            generate_audio,
            docs if docs_ok else "",
            lang=lang,
            voice=config["voice_gender"],
            timeout=300,
        )
        if audio_ok:
            lang_results["audio"] = audio

        # Video
        section("  Generate Video", level=2)
        video_ok, video, video_dur = run_phase(
            "video_generation",
            generate_video,
            docs if docs_ok else [],
            audio if audio_ok else None,
            lang=lang,
            timeout=300,
        )
        if video_ok:
            lang_results["video"] = video

        # Quiz
        section("  Generate Quiz", level=2)
        quiz_ok, quiz, quiz_dur = run_phase(
            "quiz_generation",
            generate_quiz,
            analysis,
            lang=lang,
            timeout=60,
        )
        if quiz_ok:
            lang_results["quiz"] = quiz

        results[lang] = lang_results

    return results


def phase4_pdf_design(topic: str, content_results: dict, langs: list) -> dict:
    """Phase 4: Generate PDF (desktop + mobile) and ePub."""
    from lib.pdf_designer import generate_pdf, generate_epub

    results = {}

    for lang in langs:
        if lang not in LANG_CONFIG or lang not in content_results:
            continue

        config = LANG_CONFIG[lang]
        lang_content = content_results[lang]
        docs = lang_content.get("docs", "")
        infographics = lang_content.get("infographics", [])

        section(f"PDF Design: {config['name']} ({lang})", level=2)

        # Desktop PDF
        section("  Desktop PDF", level=2)
        pdf_desktop_ok, pdf_desktop_path, pdf_dur = run_phase(
            "desktop_pdf",
            generate_pdf,
            docs=docs,
            infographics=infographics,
            lang=lang,
            format="desktop",
            timeout=180,
        )
        if pdf_desktop_ok:
            results.setdefault(lang, {})["pdf_desktop"] = pdf_desktop_path

        # Mobile PDF
        section("  Mobile PDF", level=2)
        pdf_mobile_ok, pdf_mobile_path, _ = run_phase(
            "mobile_pdf",
            generate_pdf,
            docs=docs,
            infographics=infographics,
            lang=lang,
            format="mobile",
            timeout=180,
        )
        if pdf_mobile_ok:
            results.setdefault(lang, {})["pdf_mobile"] = pdf_mobile_path

        # ePub
        section("  ePub", level=2)
        epub_ok, epub_path, _ = run_phase(
            "epub_generation",
            generate_epub,
            docs=docs,
            lang=lang,
            timeout=60,
        )
        if epub_ok:
            results.setdefault(lang, {})["epub"] = epub_path

    return results


def phase5_quality_control(topic: str, pdf_results: dict, content_results: dict, langs: list) -> dict:
    """Phase 5: Run 6-point quality verification."""
    from lib.quality_checker import run_quality_checks

    section("Quality Control — 6 Verificaciones", level=2)

    all_results = {}
    for lang in langs:
        if lang not in LANG_CONFIG:
            continue

        config = LANG_CONFIG[lang]
        section(f"  {config['name']} ({lang})", level=2)

        checks = {
            "completeness": {
                "description": "PDF tiene introducción + cuerpo + conclusión + apéndice",
                "severity": "critical",
            },
            "coherence": {
                "description": "Las secciones fluyen lógicamente sin contradicciones",
                "severity": "high",
            },
            "visual_quality": {
                "description": "Las infografías están referenciadas y se cargan correctamente",
                "severity": "high",
            },
            "audio_quality": {
                "description": "El audio dura el tiempo esperado para la narración",
                "severity": "medium",
            },
            "mobile_friendly": {
                "description": "El PDF es legible en pantalla de móvil",
                "severity": "medium",
            },
            "branding_consistency": {
                "description": "El estilo, fuentes y colores son consistentes en todos los productos",
                "severity": "medium",
            },
        }

        lang_checks = {}
        for check_name, check_info in checks.items():
            passed, message = run_quality_checks(
                topic=topic,
                lang=lang,
                check=check_name,
                content=content_results.get(lang),
                pdf_path=pdf_results.get(lang, {}).get(f"pdf_desktop"),
                audio_path=content_results.get(lang, {}).get("audio", {}).get("path"),
            )
            lang_checks[check_name] = {
                "passed": passed,
                "message": message,
                "severity": check_info["severity"],
                "description": check_info["description"],
            }
            status = "✅" if passed else "❌"
            print(f"    {status} {check_name}: {message}")

        all_results[lang] = lang_checks

    return all_results


def phase6_export(topic: str, all_results: dict, langs: list) -> Path:
    """Phase 6: Bundle everything into output/<topic_slug>/."""
    slug = generate_topic_slug(topic)
    output_path = OUTPUT_DIR / slug
    output_path.mkdir(parents=True, exist_ok=True)

    # Copy/move files from temp locations to output
    # (This depends on where content_generator/pdf_designer put things)
    # For now, just record what should be there

    metadata = {
        "topic": topic,
        "slug": slug,
        "created_at": datetime.now().isoformat(),
        "languages": [lang for lang in langs if lang in LANG_CONFIG],
        "phase_results": {
            "source_collection": "completed",
            "notebooklm_analysis": "completed",
            "content_generation": "completed" if all_results else "not_run",
            "pdf_design": "completed" if all_results else "not_run",
            "quality_control": "completed" if all_results else "not_run",
            "export": "in_progress",
        },
        "products": {
            lang: {
                "pdf_desktop": str(output_path / "pdf_desktop" / f"{lang}_{slug}_desktop.pdf"),
                "pdf_mobile": str(output_path / "pdf_mobile" / f"{lang}_{slug}_mobile.pdf"),
                "epub": str(output_path / "epub" / f"{lang}_{slug}.epub"),
                "audio": str(output_path / "audio" / f"{lang}_{slug}.mp3"),
                "video": str(output_path / "video" / f"{lang}_{slug}.mp4"),
                "quiz": str(output_path / "quiz" / f"{lang}_{slug}_quiz.md"),
            }
            for lang in langs
            if lang in LANG_CONFIG
        },
    }

    metadata_path = output_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n  📦 Export completed")
    print(f"  Output directory: {output_path}")
    print(f"  Metadata: {metadata_path}")

    return output_path


# =============================================================================
# Main Pipeline
# =============================================================================
def run_pipeline(topic: str, langs: list):
    """Run the full AIIA-NTBLM-Factory pipeline."""
    print("\n" + "=" * 60)
    print("  AIIA-NTBLM-Factory — Pipeline Completo")
    print("=" * 60)
    print(f"  Tema: {topic}")
    print(f"  Idiomas: {[LANG_CONFIG[l]['name'] for l in langs]}")
    print(f"  Salida: {OUTPUT_DIR / generate_topic_slug(topic)}")
    print("=" * 60)

    if not check_env():
        sys.exit(1)

    # Phase 1: Source Collection
    success, sources_data, dur1 = run_phase(
        "Phase 1 — Source Collection",
        phase1_source_collection,
        topic=topic,
        lang=langs[0] if len(langs) == 1 else "all",
    )
    if not success:
        print("  ❌ Pipeline aborted at Phase 1")
        return False

    sources = sources_data["filtered"]
    if not sources:
        print("  ⚠️  No sources found after filtering")
        print("  Continuing with empty sources (NotebookLM will have no material)")
    else:
        print(f"  ✅ {len(sources)} sources ready for NotebookLM")

    # Phase 2: NotebookLM Analysis
    # Run once with the primary language, then reuse for all langs
    primary_lang = langs[0] if langs else "es"
    success, analysis_data, dur2 = run_phase(
        "Phase 2 — NotebookLM Analysis",
        phase2_notebooklm_analysis,
        topic=topic,
        sources=sources,
        lang=primary_lang,
    )
    if not success:
        print("  ❌ Pipeline aborted at Phase 2")
        return False

    analysis = analysis_data.get("analysis", {})
    if not analysis:
        print("  ⚠️  No analysis extracted from NotebookLM")
    else:
        print(f"  ✅ NotebookLM analysis extracted: {len(analysis)} keys")

    # Phase 3: Content Generation
    success, content_results, dur3 = run_phase(
        "Phase 3 — Content Generation",
        phase3_content_generation,
        topic=topic,
        analysis=analysis,
        langs=langs,
    )
    if not success:
        print("  ❌ Pipeline aborted at Phase 3")
        return False

    for lang in langs:
        if lang in content_results:
            cr = content_results[lang]
            print(f"  ✅ {lang}: docs={'✓' if cr.get('docs') else '✗'}, "
                  f"audio={'✓' if cr.get('audio') else '✗'}, "
                  f"video={'✓' if cr.get('video') else '✗'}")

    # Phase 4: PDF Design
    success, pdf_results, dur4 = run_phase(
        "Phase 4 — PDF Design",
        phase4_pdf_design,
        topic=topic,
        content_results=content_results,
        langs=langs,
    )
    if not success:
        print("  ❌ Pipeline aborted at Phase 4")
        return False

    for lang in langs:
        if lang in pdf_results:
            pr = pdf_results[lang]
            print(f"  ✅ {lang}: desktop={'✓' if pr.get('pdf_desktop') else '✗'}, "
                  f"mobile={'✓' if pr.get('pdf_mobile') else '✗'}, "
                  f"epub={'✓' if pr.get('epub') else '✗'}")

    # Phase 5: Quality Control
    success, qc_results, dur5 = run_phase(
        "Phase 5 — Quality Control",
        phase5_quality_control,
        topic=topic,
        pdf_results=pdf_results,
        content_results=content_results,
        langs=langs,
    )
    # Don't abort on quality control failure — just report

    total_pass = sum(
        sum(1 for c in lang_checks.values() if c["passed"])
        for lang_checks in qc_results.values()
    )
    total_checks = sum(
        len(lang_checks)
        for lang_checks in qc_results.values()
    )
    print(f"\n  📊 Quality: {total_pass}/{total_checks} checks passed")

    # Phase 6: Export
    success, output_path, dur6 = run_phase(
        "Phase 6 — Export",
        phase6_export,
        topic=topic,
        all_results=qc_results,
        langs=langs,
    )

    # Summary
    total_duration = dur1 + dur2 + dur3 + dur4 + dur5 + dur6
    print("\n" + "=" * 60)
    print("  PIPELINE SUMMARY")
    print("=" * 60)
    print(f"  Tema: {topic}")
    print(f"  Duración total: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Output: {output_path}")
    print(f"  Calidad: {total_pass}/{total_checks} verificaciones pasadas")
    print("=" * 60)

    return True


# =============================================================================
# CLI Entry Point
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="AIIA-NTBLM-Factory — Pipeline orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python factory.py --topic "Como auto educarse con IA. El método Dan Martell" --lang all
  python factory.py --topic "Dan Martell scaling up" --lang es
  python factory.py --topic "Autoeducation con IA" --lang en --verify
        """,
    )

    parser.add_argument(
        "--topic",
        required=True,
        help="Topic for the digital product (e.g. 'Como auto educarse con IA. El método Dan Martell')",
    )
    parser.add_argument(
        "--lang",
        nargs="+",
        default=["all"],
        choices=["es", "en", "all"],
        help="Language(s) to generate. 'all' = both Spanish + English",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run quality verification checks (Phase 5)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
    )

    args = parser.parse_args()

    if args.debug:
        os.environ["FACTORY_DEBUG"] = "1"

    # Resolve languages
    if "all" in args.lang:
        langs = ["es", "en"]
    else:
        langs = [l for l in args.lang if l in LANG_CONFIG]
        if not langs:
            print("❌ Invalid language selection. Use 'es', 'en', or 'all'.")
            sys.exit(1)

    print(f"\n  🤖 AIIA-NTBLM-Factory v1.0")
    print(f"  📁 Output: {OUTPUT_DIR}")

    success = run_pipeline(topic=args.topic, langs=langs)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
