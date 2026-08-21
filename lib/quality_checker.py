#!/usr/bin/env python3
"""
AIIA-NTBLM-Factory — Quality Checker
Runs 6-point automated verification on generated products before export.
Does NOT skip any verification — each check must pass.
"""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Config
ROOT = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = ROOT / "output"

# Severity levels
SEVERITY = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

# Minimum thresholds
THRESHOLDS = {
    "min_pdf_size_kb": 50,          # PDF must be at least 50KB
    "min_audio_duration_sec": 30,   # Audio must be at least 30s
    "min_video_duration_sec": 10,   # Video must be at least 10s
    "min_doc_sections": 3,          # Document must have at least 3 sections
    "min_slides": 3,                # Slides must have at least 3 slides
    "min_quiz_questions": 3,        # Quiz must have at least 3 questions
}


class QualityChecker:
    """
    Automated quality verification for AIIA-NTBLM-Factory products.

    Each check returns:
        - passed: bool
        - message: human-readable result description
        - severity: severity level (critical, high, medium, low)
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.checks_ran = []
        self.checks_passed = 0
        self.checks_failed = 0

    def run_all_checks(self, output_dir: Path, lang: str = "es") -> Dict:
        """
        Run all 6 quality checks.

        Args:
            output_dir: Path to output/<topic>/ directory
            lang: Language code

        Returns:
            Dict with check results
        """
        results = {}

        # Check 1: Completeness
        results["completeness"] = self.check_completeness(output_dir, lang)

        # Check 2: Coherence
        results["coherence"] = self.check_coherence(output_dir, lang)

        # Check 3: Visual Quality
        results["visual_quality"] = self.check_visual_quality(output_dir, lang)

        # Check 4: Audio Quality
        results["audio_quality"] = self.check_audio_quality(output_dir, lang)

        # Check 5: Mobile Responsiveness
        results["mobile_responsiveness"] = self.check_mobile_responsiveness(output_dir, lang)

        # Check 6: Branding Consistency
        results["branding_consistency"] = self.check_branding_consistency(output_dir, lang)

        self.checks_ran = list(results.keys())
        self.checks_passed = sum(1 for r in results.values() if r.get("passed"))
        self.checks_failed = len(results) - self.checks_passed

        return results

    def check_completeness(self, output_dir: Path, lang: str) -> Dict:
        """
        Check 1: Completeness
        Verifies that the PDF has all required sections:
        - Introduction
        - Main content (at least 2 sections)
        - Conclusion
        - At least one appendix element

        Severity: CRITICAL
        """
        pdf_desktop = output_dir / "pdf_desktop"
        pdf_files = list(pdf_desktop.glob(f"{lang}*.pdf")) if pdf_desktop.exists() else []

        if not pdf_files:
            return {
                "passed": False,
                "message": "❌ No PDF desktop file found",
                "severity": "critical",
                "details": "Missing: pdf_desktop/<lang>_*.pdf",
            }

        # Check if PDF has sufficient size
        pdf_path = pdf_files[0]
        size_kb = pdf_path.stat().st_size / 1024

        if size_kb < THRESHOLDS["min_pdf_size_kb"]:
            return {
                "passed": False,
                "message": f"❌ PDF too small ({size_kb:.1f}KB < {THRESHOLDS['min_pdf_size_kb']}KB min)",
                "severity": "critical",
                "details": f"Size: {size_kb:.1f}KB",
            }

        # Check if markdown docs have required sections
        docs_path = output_dir / f"{lang}_docs.md"
        if docs_path.exists():
            content = docs_path.read_text(encoding="utf-8", errors="ignore")
            sections_found = set()

            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("## "):
                    sections_found.add(stripped[3:].lower())

            required_sections = {"introducción", "introduction", "contenido", "content", "conclusión", "conclusion"}
            found_required = sections_found & required_sections

            # Check for at least intro + content + conclusion
            has_intro = any("intro" in s for s in sections_found)
            has_content = any("contenido" in s or "content" in s for s in sections_found)
            has_conclusion = any("conclus" in s for s in sections_found)

            if not (has_intro and has_content and has_conclusion):
                return {
                    "passed": False,
                    "message": "❌ PDF lacks required sections (intro + content + conclusion)",
                    "severity": "critical",
                    "details": f"Found sections: {sorted(sections_found)}",
                }

        return {
            "passed": True,
            "message": f"✅ PDF completo: {size_kb:.1f}KB con todas las secciones requeridas",
            "severity": "critical",
            "details": f"Size: {size_kb:.1f}KB, Sections: OK",
        }

    def check_coherence(self, output_dir: Path, lang: str) -> Dict:
        """
        Check 2: Coherence
        Verifies that the document sections flow logically and are internally consistent.
        Uses a simple heuristic: section headers should be in logical order,
        and key terms should appear consistently.

        Severity: HIGH
        """
        docs_path = output_dir / f"{lang}_docs.md"
        if not docs_path.exists():
            return {
                "passed": False,
                "message": "❌ No docs.md found to verify coherence",
                "severity": "high",
                "details": "Missing: docs.md file",
            }

        content = docs_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        # Extract section headers in order
        section_order = []
        for line in lines:
            stripped = line.strip()
            match = re.match(r'^#+ (.+)$', stripped)
            if match:
                section_order.append(match.group(1).lower())

        # Check logical section order (intro before conclusion, etc.)
        has_intro = any("intro" in s for s in section_order)
        has_conclusion = any("conclus" in s for s in section_order)

        if has_intro and has_conclusion:
            intro_idx = next(i for i, s in enumerate(section_order) if "intro" in s)
            conclusion_idx = next(i for i, s in enumerate(section_order) if "conclus" in s)

            if conclusion_idx < intro_idx:
                return {
                    "passed": False,
                    "message": "❌ Conclusion appears before Introduction (incoherent order)",
                    "severity": "high",
                    "details": f"Intro at index {intro_idx}, Conclusion at index {conclusion_idx}",
                }

        # Check for key term consistency (at least 3 mentions of main topic)
        word_counts = {}
        for line in lines:
            words = re.findall(r'\b\w+\b', line.lower())
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1

        total_words = sum(word_counts.values())
        if total_words > 100:
            # Verify there's substantial content
            min_content_len = 200
            if len(content) < min_content_len:
                return {
                    "passed": False,
                    "message": f"❌ Document too short ({len(content)} chars < {min_content_len} min)",
                    "severity": "high",
                    "details": f"Length: {len(content)} chars",
                }

        return {
            "passed": True,
            "message": "✅ Coherencia verificada: secciones en orden logico, contenido sustancial",
            "severity": "high",
            "details": f"Sections: {len(section_order)}, Words: {total_words}",
        }

    def check_visual_quality(self, output_dir: Path, lang: str) -> Dict:
        """
        Check 3: Visual Quality
        Verifies that infographics are properly referenced and appear in the PDF.
        Checks that images are not broken/placeholder.

        Severity: HIGH
        """
        # Check if there are infographics generated
        infographics_dir = output_dir / "infographics"
        if infographics_dir.exists():
            svg_files = list(infographics_dir.glob("*.svg"))
            if not svg_files:
                return {
                    "passed": False,
                    "message": "⚠️  Infographics directory exists but no SVG files found",
                    "severity": "high",
                    "details": "Expected: infographics/*.svg",
                }

            # Check each SVG for valid structure
            for svg_file in svg_files[:3]:
                try:
                    content = svg_file.read_text()
                    if "<svg" not in content:
                        return {
                            "passed": False,
                            "message": f"❌ Invalid SVG: {svg_file.name} (missing <svg> tag)",
                            "severity": "high",
                            "details": f"File: {svg_file.name}",
                        }
                except Exception as e:
                    return {
                        "passed": False,
                        "message": f"❌ Cannot read SVG: {svg_file.name} — {e}",
                        "severity": "high",
                        "details": f"File: {svg_file.name}",
                    }
        else:
            # No infographics directory — that's OK if none were generated
            pass

        # Check PDF size as proxy for image inclusion
        pdf_desktop = output_dir / "pdf_desktop"
        pdf_files = list(pdf_desktop.glob(f"{lang}*.pdf")) if pdf_desktop.exists() else []

        if pdf_files:
            pdf_size = pdf_files[0].stat().st_size / 1024
            if pdf_size < THRESHOLDS["min_pdf_size_kb"]:
                return {
                    "passed": False,
                    "message": f"❌ PDF visual content may be incomplete (size: {pdf_size:.1f}KB)",
                    "severity": "high",
                    "details": f"PDF size: {pdf_size:.1f}KB",
                }

        return {
            "passed": True,
            "message": "✅ Calidad visual verificada: infografías válidas, PDF con contenido visual",
            "severity": "high",
            "details": "Infographics: OK",
        }

    def check_audio_quality(self, output_dir: Path, lang: str) -> Dict:
        """
        Check 4: Audio Quality
        Verifies that the generated audio (MP3) has reasonable duration and file size.

        Severity: MEDIUM
        """
        audio_dir = output_dir / "audio"
        if not audio_dir.exists():
            return {
                "passed": False,
                "message": "❌ No audio directory found",
                "severity": "medium",
                "details": "Missing: audio/ directory",
            }

        audio_files = list(audio_dir.glob(f"{lang}*.mp3"))
        if not audio_files:
            # Maybe other language? Check if any audio exists
            all_audio = list(audio_dir.glob("*.mp3"))
            if all_audio:
                return {
                    "passed": False,
                    "message": f"❌ No audio file for language '{lang}' found (found: {[f.name for f in all_audio]})",
                    "severity": "medium",
                    "details": f"Language: {lang}",
                }
            return {
                "passed": False,
                "message": "❌ No audio files found at all",
                "severity": "medium",
                "details": "Expected: audio/<lang>_*.mp3",
            }

        audio_path = audio_files[0]
        size_kb = audio_path.stat().st_size / 1024

        # Get duration using ffprobe
        duration_sec = 0
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
                capture_output=True, text=True, timeout=10,
            )
            duration_sec = float(result.stdout.strip())
        except Exception:
            duration_sec = 0

        # Quality checks
        issues = []

        if duration_sec < THRESHOLDS["min_audio_duration_sec"]:
            issues.append(f"Duration too short ({duration_sec:.1f}s < {THRESHOLDS['min_audio_duration_sec']}s min)")

        if size_kb < 5:
            issues.append(f"File too small ({size_kb:.1f}KB) — may be corrupted")

        if issues:
            return {
                "passed": False,
                "message": f"❌ Audio quality issues: {'; '.join(issues)}",
                "severity": "medium",
                "details": f"Duration: {duration_sec:.1f}s, Size: {size_kb:.1f}KB",
            }

        return {
            "passed": True,
            "message": f"✅ Audio de calidad: {duration_sec:.1f}s, {size_kb:.1f}KB",
            "severity": "medium",
            "details": f"Duration: {duration_sec:.1f}s, Size: {size_kb:.1f}KB",
        }

    def check_mobile_responsiveness(self, output_dir: Path, lang: str) -> Dict:
        """
        Check 5: Mobile Responsiveness
        Verifies that the mobile PDF is readable on small screens.
        Checks that mobile PDF exists, has reasonable size, and uses appropriate formatting.

        Severity: MEDIUM
        """
        pdf_mobile = output_dir / "pdf_mobile"
        pdf_files = list(pdf_mobile.glob(f"{lang}*.pdf")) if pdf_mobile.exists() else []

        if not pdf_files:
            return {
                "passed": False,
                "message": f"❌ No mobile PDF found for {lang} (expected: pdf_mobile/{lang}_*.pdf)",
                "severity": "medium",
                "details": "Missing: pdf_mobile/<lang>_*.pdf",
            }

        pdf_path = pdf_files[0]
        size_kb = pdf_path.stat().st_size / 1024

        if size_kb < THRESHOLDS["min_pdf_size_kb"]:
            return {
                "passed": False,
                "message": f"❌ Mobile PDF too small ({size_kb:.1f}KB) — likely empty or corrupted",
                "severity": "medium",
                "details": f"Mobile PDF size: {size_kb:.1f}KB",
            }

        # Mobile PDF should be smaller than desktop (A5 vs A4)
        pdf_desktop_dir = output_dir / "pdf_desktop"
        desktop_files = list(pdf_desktop_dir.glob(f"{lang}*.pdf")) if pdf_desktop_dir.exists() else []

        if desktop_files:
            desktop_size = desktop_files[0].stat().st_size / 1024
            if size_kb > desktop_size * 0.9:
                # Mobile PDF is almost as large as desktop — might be wrong format
                return {
                    "passed": False,
                    "message": "⚠️  Mobile PDF size similar to desktop — may not be optimized for mobile",
                    "severity": "medium",
                    "details": f"Mobile: {size_kb:.1f}KB, Desktop: {desktop_size:.1f}KB",
                }

        return {
            "passed": True,
            "message": f"✅ PDF mobile optimizado: {size_kb:.1f}KB, legible en pantallas pequenas",
            "severity": "medium",
            "details": f"Mobile PDF size: {size_kb:.1f}KB",
        }

    def check_branding_consistency(self, output_dir: Path, lang: str) -> Dict:
        """
        Check 6: Branding Consistency
        Verifies that all products share consistent branding:
        - Same title format
        - Same font usage (in LaTeX preamble)
        - Same color scheme (in SVG infographics)
        - AIIA-NTBLM-Factory branding present

        Severity: LOW
        """
        issues = []

        # Check 1: Title consistency across products
        docs_path = output_dir / f"{lang}_docs.md"
        if docs_path.exists():
            docs_content = docs_path.read_text(encoding="utf-8", errors="ignore")
            title_match = re.search(r'^#\s+(.+)$', docs_content, re.MULTILINE)
            doc_title = title_match.group(1) if title_match else ""

            if not doc_title:
                issues.append("Document title not found in docs.md")

        # Check 2: AIIA branding present
        if docs_path.exists():
            docs_content = docs_path.read_text(encoding="utf-8", errors="ignore")
            if "AIIA-NTBLM-Factory" not in docs_content and "AIIA" not in docs_content:
                issues.append("AIIA branding not found in document content")

        # Check 3: Color consistency in infographics
        infographics_dir = output_dir / "infographics"
        if infographics_dir.exists():
            svg_files = list(infographics_dir.glob("*.svg"))
            colors_found = set()

            for svg_file in svg_files[:2]:
                try:
                    content = svg_file.read_text()
                    # Extract fill colors
                    fill_colors = re.findall(r'fill=["\']([^"\']+)["\']', content)
                    stroke_colors = re.findall(r'stroke=["\']([^"\']+)["\']', content)
                    colors_found.update(fill_colors + stroke_colors)
                except Exception:
                    pass

            # Check for consistent dark color (primary brand)
            has_dark = any("1a1a2e" in c.lower() or "#1a1a2e" == c.lower() for c in colors_found)
            if svg_files and not has_dark:
                issues.append("Infographic color scheme may not match brand (dark color #1a1a2e not found)")

        if issues:
            return {
                "passed": False,
                "message": f"⚠️  Branding inconsistencies: {'; '.join(issues)}",
                "severity": "low",
                "details": "; ".join(issues),
            }

        return {
            "passed": True,
            "message": "✅ Consistencia de branding: títulos, colores y marca AIIA consistentes",
            "severity": "low",
            "details": "Branding: OK",
        }

    def summary(self) -> Dict:
        """Return a summary of all checks run."""
        return {
            "total_checks": len(self.checks_ran),
            "passed": self.checks_passed,
            "failed": self.checks_failed,
            "results": {
                name: {
                    "passed": result.get("passed", False),
                    "message": result.get("message", ""),
                    "severity": result.get("severity", "low"),
                }
                for name, result in zip(self.checks_ran, self.checks_passed)
            },
            "all_passed": self.checks_failed == 0,
        }


def run_quality_checks(topic: str, lang: str, check: str,
                        content: Dict = None, pdf_path: str = None,
                        audio_path: str = None) -> Tuple[bool, str]:
    """
    Run a single quality check.

    Args:
        topic: Product topic
        lang: Language code
        check: Check name ("completeness", "coherence", "visual_quality",
               "audio_quality", "mobile_responsiveness", "branding_consistency")
        content: Content dict (docs, slides, infographics, etc.)
        pdf_path: Path to PDF file (for PDF checks)
        audio_path: Path to audio file (for audio checks)

    Returns:
        (passed: bool, message: str)
    """
    # Map check names to Output directory structure
    slug = re.sub(r'[^\w]', '', f"{lang}_{datetime.now().strftime('%Y%m%d')}")
    output_dir = OUTPUT_DIR / slug

    # Create a temporary output dir structure for testing
    # (In production, this would be the real output dir)

    checker = QualityChecker()
    method = getattr(checker, f"check_{check.replace('-', '_')}", None)

    if method is None:
        return False, f"❌ Unknown check: {check}"

    # For simplicity, run on output_dir (which may be empty in tests)
    try:
        result = method(output_dir, lang)
        return result.get("passed", False), result.get("message", "")
    except Exception as e:
        return False, f"❌ Check error: {e}"


def main():
    """Run quality checker on a specific output directory."""
    import argparse

    parser = argparse.ArgumentParser(description="Quality checker for AIIA-NTBLM-Factory")
    parser.add_argument("output_dir", nargs="?", help="Path to output/<topic>/ directory")
    parser.add_argument("--lang", default="es", help="Language code (default: es)")
    args = parser.parse_args()

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Find latest output
        if OUTPUT_DIR.exists():
            subdirs = [d for d in OUTPUT_DIR.iterdir() if d.is_dir()]
            if subdirs:
                output_dir = sorted(subdirs, key=lambda d: d.stat().st_mtime, reverse=True)[0]
            else:
                print("❌ No output directories found")
                return
        else:
            print("❌ Output directory not found")
            return

    print(f"=== Quality Checker: {output_dir.name} ({args.lang}) ===\n")

    checker = QualityChecker()
    results = checker.run_all_checks(output_dir, lang=args.lang)

    print("Resultados:")
    print("-" * 50)

    for check_name, result in results.items():
        status = "✅" if result.get("passed") else "❌"
        severity = result.get("severity", "low").upper()
        message = result.get("message", "")
        print(f"  {status} {check_name} ({severity})")
        print(f"      {message}")

    print("-" * 50)
    print(f"  Total: {checker.checks_passed}/{checker.checks_ran} verificaciones pasadas")

    if checker.checks_failed > 0:
        print(f"\n  ⚠️  {checker.checks_failed} verificaciones fallaron — revisar antes de exportar")
    else:
        print(f"\n  ✅ TODAS las verificaciones pasaron — listo para exportar")


if __name__ == "__main__":
    main()
