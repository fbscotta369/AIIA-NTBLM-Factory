#!/usr/bin/env python3
"""
AIIA-NTBLM-Factory — PDF Designer (simplified)
Generates PDF (desktop + mobile) and ePub from Markdown content.
Uses pandoc as primary engine (simpler, no LaTeX escaping issues).
Falls back to simple HTML→PDF if pandoc unavailable.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

ROOT = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = ROOT / "output"


def generate_pdf(docs: str, infographics: List[Dict], lang: str, fmt: str = "desktop") -> str:
    """
    Generate PDF from markdown content using pandoc (preferred) or simple fallback.

    Args:
        docs: Markdown content string
        infographics: List of infographic dicts (may be empty)
        lang: Language code (es/en)
        fmt: "desktop" or "mobile"

    Returns:
        Path to generated PDF file, or empty string on failure
    """
    lang_name = {"es": "Spanish", "en": "English"}.get(lang, lang)

    # Extract title
    title_match = re.search(r'^#\s+(.+)$', docs, re.MULTILINE)
    title = title_match.group(1) if title_match else f"Documento {lang_name}"

    # Create output directory
    output_dir = OUTPUT_DIR / ("pdf_desktop" if fmt == "desktop" else "pdf_mobile")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Filename
    slug = re.sub(r'[^\w]', '', f"{lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_path = output_dir / f"{slug}.pdf"

    # Strategy: pandoc with wkhtmltopdf or weasyprint, or simple HTML fallback
    success = False
    method = None

    # Method 1: pandoc with HTML output + wkhtmltopdf
    if shutil_which("wkhtmltopdf"):
        success, method = pandoc_html_to_pdf(docs, output_path, lang, title)
        if success:
            print(f"  📄 PDF Desktop generado con pandoc+wkhtmltopdf: {output_path}")
            return str(output_path)

    # Method 2: pandoc direct to PDF (needs LaTeX)
    if shutil_which("pandoc") and shutil_which("pdflatex"):
        success, method = pandoc_direct_pdf(docs, output_path, lang, title)
        if success:
            print(f"  📄 PDF generado con pandoc+LaTeX: {output_path}")
            return str(output_path)

    # Method 3: pandoc to HTML, then weasyprint
    if shutil_which("pandoc") and shutil_which("weasyprint"):
        success, method = pandoc_html_weasyprint(docs, output_path, lang, title)
        if success:
            print(f"  📄 PDF generado con pandoc+weasyprint: {output_path}")
            return str(output_path)

    # Method 4: Simple HTML → PDF via weasyprint (no pandoc)
    if shutil_which("weasyprint"):
        success, method = simple_html_to_pdf(docs, output_path, lang, title, fmt)
        if success:
            print(f"  📄 PDF generado con HTML+weasyprint: {output_path}")
            return str(output_path)

    # Method 5: Pure Python fallback with reportlab
    try:
        import reportlab
        success, method = reportlab_pdf(docs, output_path, lang, title, fmt)
        if success:
            print(f"  📄 PDF generado con reportlab: {output_path}")
            return str(output_path)
    except ImportError:
        pass

    print(f"  ❌ No se pudo generar PDF. Instala: pandoc, wkhtmltopdf, weasyprint, o reportlab")
    return ""


def generate_epub(docs: str, lang: str) -> str:
    """Generate ePub from markdown using pandoc."""
    slug = re.sub(r'[^\w]', '', f"{lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    output_dir = OUTPUT_DIR / "epub"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}.epub"

    if not shutil_which("pandoc"):
        print("  ⚠️  pandoc no disponible para ePub generation")
        return ""

    # Write markdown to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(docs)
        md_file = Path(f.name)

    try:
        cmd = [
            "pandoc", str(md_file),
            "-o", str(output_path),
            "--toc",
            "--standalone",
            "-V", f"lang={lang}",
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if proc.returncode == 0 and output_path.exists():
            print(f"  📖 ePub generado: {output_path}")
            return str(output_path)
        else:
            print(f"  ❌ ePub fallo: {proc.stderr[:200]}")
            return ""
    finally:
        md_file.unlink(missing_ok=True)


def test_pdf_generation():
    """Quick test of PDF generation."""
    print("=== PDF Designer Test ===")
    print(f"  pandoc available: {bool(shutil_which('pandoc'))}")
    print(f"  wkhtmltopdf available: {bool(shutil_which('wkhtmltopdf'))}")
    print(f"  weasyprint available: {bool(shutil_which('weasyprint'))}")
    print(f"  pdflatex available: {bool(shutil_which('pdflatex'))}")

    sample_docs = """# Documento de Prueba

## Introduccion
Este es un documento de prueba del sistema AIIA-NTBLM-Factory.

## Contenido Principal
- Idea 1: Contenido importante
- Idea 2: Otro concepto clave
- Idea 3: Tema relevante

## Conclusión
El documento de prueba funciona correctamente.
"""

    print("\n  📄 Probando generacion de PDF...")
    result = generate_pdf(sample_docs, [], lang="es", fmt="desktop")
    if result:
        print(f"    ✅ Exito: {result}")
    else:
        print("    ❌ No se pudo generar PDF con ningun metodo disponible")

    print("\n  📖 Probando generacion de ePub...")
    epub = generate_epub(sample_docs, lang="es")
    if epub:
        print(f"    ✅ ePub: {epub}")
    else:
        print("    ❌ No se pudo generar ePub")


# =============================================================================
# Internal helpers
# =============================================================================

def shutil_which(name: str) -> bool:
    """Check if a command is available."""
    import shutil
    return shutil.which(name) is not None


def pandoc_html_to_pdf(docs: str, output: Path, lang: str, title: str) -> tuple:
    """Method 1: pandoc → HTML → wkhtmltopdf."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            html_file = Path(f.name)

        cmd_pandoc = ["pandoc", "-f", "markdown", "-t", "html5", "-s", "-o", str(html_file)]
        proc1 = subprocess.run(cmd_pandoc, input=docs.encode(), capture_output=True, timeout=30)
        if proc1.returncode != 0:
            return False, "pandoc HTML conversion failed"

        cmd_wkhtml = ["wkhtmltopdf", "--quiet", "--print-media-type", str(html_file), str(output)]
        proc2 = subprocess.run(cmd_wkhtml, capture_output=True, timeout=60)
        html_file.unlink(missing_ok=True)

        if proc2.returncode == 0 and output.exists():
            return True, "wkhtmltopdf"
        return False, f"wkhtmltopdf failed: {proc2.stderr[:200]}"
    except Exception as e:
        return False, str(e)


def pandoc_direct_pdf(docs: str, output: Path, lang: str, title: str) -> tuple:
    """Method 2: pandoc direct to PDF (needs LaTeX)."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(docs)
            md_file = Path(f.name)

        cmd = [
            "pandoc", str(md_file),
            "-o", str(output),
            "--pdf-engine=pdflatex",
            "-V", f"lang={lang}",
            "-V", "geometry:margin=2cm",
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        md_file.unlink(missing_ok=True)

        if proc.returncode == 0 and output.exists():
            return True, "LaTeX"
        return False, f"pandoc LaTeX failed: {proc.stderr[:300]}"
    except Exception as e:
        return False, str(e)


def pandoc_html_weasyprint(docs: str, output: Path, lang: str, title: str) -> tuple:
    """Method 3: pandoc → HTML → weasyprint."""
    try:
        # Pandoc to HTML with embedded CSS
        html_content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'DejaVu Sans', sans-serif; line-height: 1.6; color: #1a1a2e; }}
  h1 {{ color: #1a1a2e; border-bottom: 2px solid #4a90d9; padding-bottom: 8px; }}
  h2 {{ color: #1a1a2e; margin-top: 24px; }}
  h3 {{ color: #333; }}
  p {{ margin: 8px 0; }}
  ul {{ margin: 8px 0; }}
  li {{ margin: 4px 0; }}
  blockquote {{ border-left: 4px solid #4a90d9; padding-left: 16px; color: #666; margin: 16px 0; }}
  code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
  a {{ color: #4a90d9; }}
  @page {{ size: A4; margin: 2cm; @bottom-center {{ content: counter(page); }} }}
</style>
</head>
<body>
{docs}
</body>
</html>"""

        cmd = ["weasyprint", "-", str(output)]
        proc = subprocess.run(cmd, input=html_content.encode(), capture_output=True, text=True, timeout=60)

        if proc.returncode == 0 and output.exists():
            return True, "weasyprint"
        return False, f"weasyprint failed: {proc.stderr[:200]}"
    except Exception as e:
        return False, str(e)


def simple_html_to_pdf(docs: str, output: Path, lang: str, title: str, fmt: str) -> tuple:
    """Method 4: Convert markdown to simple HTML, then weasyprint."""
    try:
        # Simple markdown to HTML converter
        html_body = markdown_to_html(docs)

        page_size = "A4" if fmt == "desktop" else "A5"
        margin = "2cm" if fmt == "desktop" else "1.2cm"
        font_size = "12pt" if fmt == "desktop" else "10pt"

        html_content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<style>
  @page {{ size: {page_size}; margin: {margin}; }}
  body {{ font-family: 'DejaVu Sans', sans-serif; font-size: {font_size}; line-height: 1.5; color: #1a1a2e; margin: 0; padding: 0; }}
  h1 {{ color: #1a1a2e; font-size: 1.8em; border-bottom: 2px solid #4a90d9; padding-bottom: 6px; margin-top: 24px; }}
  h2 {{ color: #1a1a2e; font-size: 1.3em; margin-top: 20px; }}
  h3 {{ color: #333; font-size: 1.1em; }}
  p {{ margin: 6px 0; }}
  ul {{ margin: 6px 0; padding-left: 24px; }}
  li {{ margin: 3px 0; }}
  blockquote {{ border-left: 3px solid #4a90d9; padding-left: 12px; color: #666; margin: 12px 0; }}
  code {{ background: #f5f5f5; padding: 1px 4px; border-radius: 2px; font-size: 0.9em; }}
  a {{ color: #4a90d9; text-decoration: none; }}
  @bottom-center {{ content: counter(page); font-size: 0.8em; color: #888; }}
</style>
<title>{title}</title>
</head>
<body>
<div style="text-align: center; margin-bottom: 32px; color: #888; font-size: 0.9em;">
  AIIA-NTBLM-Factory v1.0 | {title}
</div>
{html_body}
</body>
</html>"""

        cmd = ["weasyprint", "-", str(output)]
        proc = subprocess.run(cmd, input=html_content.encode(), capture_output=True, text=True, timeout=60)

        if proc.returncode == 0 and output.exists():
            return True, "HTML+weasyprint"
        return False, f"weasyprint failed: {proc.stderr[:200]}"
    except Exception as e:
        return False, str(e)


def markdown_to_html(md: str) -> str:
    """Simple markdown to HTML converter."""
    lines = md.split("\n")
    html_lines = []
    in_list = False
    list_type = None

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            if in_list:
                if list_type == "ul":
                    html_lines.append("</ul>")
                else:
                    html_lines.append("</ol>")
                in_list = False
            continue

        # Headers
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{escape_html(stripped[2:])}</h1>")
            continue
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{escape_html(stripped[3:])}</h2>")
            continue
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{escape_html(stripped[4:])}</h3>")
            continue

        # Lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
                list_type = "ul"
            html_lines.append(f"<li>{inline_markdown(stripped[2:])}</li>")
            continue
        elif stripped.startswith("1. "):
            if not in_list:
                html_lines.append("<ol>")
                in_list = True
                list_type = "ol"
            html_lines.append(f"<li>{inline_markdown(stripped[3:])}</li>")
            continue

        # Paragraphs
        if stripped and not in_list:
            html_lines.append(f"<p>{inline_markdown(stripped)}</p>")

    # Close any open list
    if in_list:
        if list_type == "ul":
            html_lines.append("</ul>")
        else:
            html_lines.append("</ol>")

    return "\n".join(html_lines)


def inline_markdown(text: str) -> str:
    """Convert inline markdown to HTML."""
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Escape HTML entities in remaining text
    text = escape_html(text)
    return text


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def reportlab_pdf(docs: str, output: Path, lang: str, title: str, fmt: str) -> tuple:
    """Method 5: Generate PDF using reportlab (pure Python)."""
    try:
        from reportlab.lib.pagesizes import A4, A5
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        page_size = A4 if fmt == "desktop" else A5
        margin = 2*cm if fmt == "desktop" else 1.5*cm

        doc = SimpleDocTemplate(
            str(output),
            pagesize=page_size,
            leftMargin=margin,
            rightMargin=margin,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            textColor=colors.HexColor("#1a1a2e"),
            fontSize=24 if fmt == "desktop" else 18,
            spaceAfter=20,
            alignment=TA_CENTER,
        )

        h2_style = ParagraphStyle(
            "CustomH2",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#1a1a2e"),
            fontSize=16 if fmt == "desktop" else 12,
            spaceBefore=16,
            spaceAfter=8,
        )

        h3_style = ParagraphStyle(
            "CustomH3",
            parent=styles["Heading3"],
            textColor=colors.HexColor("#333333"),
            fontSize=13 if fmt == "desktop" else 10,
            spaceBefore=10,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles["Normal"],
            fontSize=11 if fmt == "desktop" else 9,
            leading=16 if fmt == "desktop" else 13,
            spaceAfter=8,
        )

        bullet_style = ParagraphStyle(
            "BulletBody",
            parent=body_style,
            leftIndent=20,
            bulletIndent=10,
        )

        story = []

        # Parse markdown and build flowables
        lines = docs.split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("# "):
                story.append(Paragraph(escape_latex(stripped[2:]), title_style))
                story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#4a90d9")))
                story.append(Spacer(1, 12))
            elif stripped.startswith("## "):
                story.append(Paragraph(escape_latex(stripped[3:]), h2_style))
                story.append(Spacer(1, 6))
            elif stripped.startswith("### "):
                story.append(Paragraph(escape_latex(stripped[4:]), h3_style))
                story.append(Spacer(1, 4))
            elif stripped.startswith("- ") or stripped.startswith("* "):
                text = inline_to_reportlab(stripped[2:])
                story.append(Paragraph(text, bullet_style, bulletText="•"))
            else:
                text = inline_to_reportlab(stripped)
                story.append(Paragraph(text, body_style))

        doc.build(story)

        if output.exists():
            return True, "reportlab"
        return False, "reportlab build failed"
    except ImportError:
        return False, "reportlab not installed"
    except Exception as e:
        return False, str(e)


def escape_latex(text: str) -> str:
    """Escape LaTeX special characters for reportlab Paragraph."""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("{", "{")
        .replace("}", "}")
        .replace("#", "#")
        .replace("$", "$")
        .replace("%", "%")
        .replace("_", "_")
        .replace("~", "~")
        .replace("^", "^")
        .replace("\\", "")
    )


def inline_to_reportlab(text: str) -> str:
    """Convert inline markdown to reportlab markup."""
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Code
    text = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", text)
    return escape_latex(text)


if __name__ == "__main__":
    test_pdf_generation()
