#!/usr/bin/env python3
"""
AIIA-NTBLM-Factory — PDF Designer
Generates PDF (desktop + mobile) and ePub from Markdown content.
Uses LaTeX (pdflatex/xelatex) for professional PDF output.
"""

import re
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


def generate_pdf(
    docs: str,
    infographics: Optional[List[Dict]] = None,
    lang: str = "es",
    fmt: str = "desktop",
) -> str:
    """
    Generate PDF from Markdown content using LaTeX.

    Args:
        docs: Markdown content string
        infographics: List of infographic dicts (may be empty)
        lang: Language code (es/en)
        fmt: "desktop" or "mobile"

    Returns:
        Path to generated PDF file, or empty string on failure
    """
    if infographics is None:
        infographics = []

    lang_name = {"es": "Espanol", "en": "English"}.get(lang, lang)
    page_size = "a4" if fmt == "desktop" else "a5"
    font_size = 11 if fmt == "desktop" else 10
    margin = "2cm" if fmt == "desktop" else "1.5cm"

    title_match = re.search(r"^#\s+(.+)$", docs, re.MULTILINE)
    title = title_match.group(1) if title_match else f"Documento {lang_name}"
    safe_title = re.sub(r"[^\w\s]", "", title)

    output_dir = Path("output") / ("pdf_desktop" if fmt == "desktop" else "pdf_mobile")
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^\w]", "", f"{lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_path = output_dir / f"{slug}.pdf"

    # Escape LaTeX special chars
    def escape(text):
        return (text.replace("\\", "")
                    .replace("&", "\\&")
                    .replace("%", "\\%")
                    .replace("$", "\\$")
                    .replace("#", "\\#")
                    .replace("_", "\\_")
                    .replace("{", "\\{")
                    .replace("}", "\\}")
                    .replace("^", "\\textasciicircum{}")
                    .replace("~", "\\textasciitilde{}"))

    # Build LaTeX document
    latex = f"""\\documentclass[{font_size}pt]{{{page_size}}}
\\usepackage[margin={margin}]{{geometry}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{xcolor}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage{{enumitem}}
\\definecolor{{navy}}{{RGB}}{{26,26,46}}
\\definecolor{{blue}}{{RGB}}{{74,144,217}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{{escape(safe_title)}}}
\\fancyhead[R]{{{fmt.upper()}}}
\\fancyfoot[C]{{\\thepage}}
\\renewcommand{{\\headrulewidth}}{{0.4pt}}

\\title{{{escape(title)}}}
\\author{{AIIA-NTBLM-Factory v1.0}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle
\\thispagestyle{{fancy}}

\\section{{Introduccion / Introduction}}
\\begin{{itemize}}
\\item Generado por AIIA-NTBLM-Factory v1.0
\\item Idioma: {lang_name} | Formato: {fmt}
\\item Voz: Femenina
\\end{{itemize}}

"""

    # Parse markdown sections
    lines = docs.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("# "):
            current_section = escape(stripped[2:])
            latex += f"\\section{{{current_section}}}\n"
        elif stripped.startswith("## "):
            current_section = escape(stripped[3:])
            latex += f"\\subsection{{{current_section}}}\n"
        elif stripped.startswith("### "):
            current_section = escape(stripped[4:])
            latex += f"\\subsubsection{{{current_section}}}\n"
        elif stripped.startswith("- ") or stripped.startswith("* "):
            item = escape(stripped[2:])
            latex += f"\\item {item}\n"
        elif stripped.startswith("> "):
            quote = escape(stripped[2:])
            latex += f"\\begin{{quote}}{quote}\\end{{quote}}\n"
        elif stripped.startswith("**") and "**" in stripped[2:]:
            parts = stripped.split("**")
            line_out = ""
            for i, p in enumerate(parts):
                if i % 2 == 1:
                    line_out += f"\\textbf{{{escape(p)}}}"
                else:
                    line_out += escape(p)
            latex += f"{line_out}\n"
        elif stripped:
            latex += f"{escape(stripped)}\n"

    # Final section
    latex += f"""
\\section{{Conclusion}}
Este documento fue generado automaticamente por AIIA-NTBLM-Factory v1.0
utilizando NotebookLM para el analisis profundo de las fuentes proporcionadas.

\\end{{document}}
"""

    # Write LaTeX file
    tex_path = output_dir / f"{slug}.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex)

    # Compile: try xelatex first (better Unicode), fall back to pdflatex
    for engine in ("xelatex", "pdflatex"):
        try:
            result = subprocess.run(
                [engine, "-interaction=nonstopmode", "-halt-on-error",
                 "-output-directory", str(output_dir), str(tex_path)],
                capture_output=True, text=True, timeout=120, check=False,
            )
            if output_path.exists() and output_path.stat().st_size > 1000:
                print(f"  PDF generado ({engine}): {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")
                return str(output_path)
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"  Error compilando con {engine}: {e}")

    # Fallback: pure-Python reportlab (no LaTeX needed)
    try:
        return _generate_pdf_reportlab(docs, lang, fmt, output_dir, slug)
    except Exception as e:
        print(f"  Error en fallback reportlab: {e}")

    print("  No se pudo generar PDF. Instala texlive-xetex o reportlab.")
    return ""


def _generate_pdf_reportlab(docs: str, lang: str, fmt: str, output_dir: Path, slug: str) -> str:
    """Pure-Python PDF fallback using reportlab (no LaTeX dependency)."""
    from reportlab.lib.pagesizes import A4, A5
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    ListFlowable, ListItem, HRFlowable)
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER

    page_size = A4 if fmt == "desktop" else A5
    margin = 2 * cm if fmt == "desktop" else 1.5 * cm
    output_path = output_dir / f"{slug}.pdf"

    doc = SimpleDocTemplate(str(output_path), pagesize=page_size,
                            leftMargin=margin, rightMargin=margin,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CT", parent=styles["Title"], textColor=colors.HexColor("#1a1a2e"),
                                 fontSize=24 if fmt == "desktop" else 18, alignment=TA_CENTER)
    h2_style = ParagraphStyle("CH2", parent=styles["Heading2"], textColor=colors.HexColor("#1a1a2e"),
                             fontSize=16 if fmt == "desktop" else 12)
    h3_style = ParagraphStyle("CH3", parent=styles["Heading3"], textColor=colors.HexColor("#333333"),
                             fontSize=13 if fmt == "desktop" else 10)
    body_style = ParagraphStyle("CB", parent=styles["Normal"], fontSize=11 if fmt == "desktop" else 9,
                               leading=16 if fmt == "desktop" else 13, spaceAfter=8)
    bullet_style = ParagraphStyle("BU", parent=body_style, leftIndent=20, bulletIndent=10)

    def esc_latex(t):
        return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    def inline_to_rl(t):
        import re
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
        return esc_latex(t)

    story = []
    for line in docs.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith("# "):
            story.append(Paragraph(esc_latex(s[2:]), title_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#4a90d9")))
            story.append(Spacer(1, 12))
        elif s.startswith("## "):
            story.append(Paragraph(esc_latex(s[3:]), h2_style))
            story.append(Spacer(1, 6))
        elif s.startswith("### "):
            story.append(Paragraph(esc_latex(s[4:]), h3_style))
            story.append(Spacer(1, 4))
        elif s.startswith("- ") or s.startswith("* "):
            story.append(Paragraph(inline_to_rl(s[2:]), bullet_style, bulletText="\u2022"))
        else:
            story.append(Paragraph(inline_to_rl(s), body_style))

    doc.build(story)
    if output_path.exists() and output_path.stat().st_size > 1000:
        print(f"  PDF generado (reportlab): {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")
        return str(output_path)
    return ""


def generate_epub(docs: str, lang: str = "es") -> str:
    """Generate ePub from Markdown content."""
    lang_name = {"es": "Espanol", "en": "English"}.get(lang, lang)
    title_match = re.search(r"^#\s+(.+)$", docs, re.MULTILINE)
    title = title_match.group(1) if title_match else f"Documento {lang_name}"

    output_dir = Path("output") / "epub"
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^\w]", "", f"{lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_path = output_dir / f"{slug}.epub"

    def esc(text):
        return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;").replace("'", "&apos;"))

    # Build HTML chapters from markdown
    chapters_html = []
    current_h1 = ""
    current_content = []

    for line in docs.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            if current_h1:
                chapters_html.append((current_h1, current_content))
            current_h1 = esc(stripped[2:])
            current_content = []
        elif stripped.startswith("## "):
            if current_h1 and not current_content:
                current_content.append(f"<h2>{esc(stripped[3:])}</h2>")
            else:
                current_content.append(f"<h3>{esc(stripped[3:])}</h3>")
        elif stripped.startswith("### "):
            current_content.append(f"<h4>{esc(stripped[4:])}</h4>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            current_content.append(f"<li>{esc(stripped[2:])}</li>")
        elif stripped.startswith("> "):
            current_content.append(f"<blockquote>{esc(stripped[2:])}</blockquote>")
        elif stripped.startswith("**") and "**" in stripped[2:]:
            parts = stripped.split("**")
            line_html = ""
            for i, p in enumerate(parts):
                if i % 2 == 1:
                    line_html += f"<strong>{esc(p)}</strong>"
                else:
                    line_html += esc(p)
            current_content.append(f"<p>{line_html}</p>")
        elif stripped:
            current_content.append(f"<p>{esc(stripped)}</p>")

    if current_h1:
        chapters_html.append((current_h1, current_content))

    # Wrap list items in <ul>
    for i, (h1, content) in enumerate(chapters_html):
        wrapped = []
        in_list = False
        for item in content:
            if item.startswith("<li>"):
                if not in_list:
                    wrapped.append("<ul>")
                    in_list = True
                wrapped.append(item)
            else:
                if in_list:
                    wrapped.append("</ul>")
                    in_list = False
                wrapped.append(item)
        if in_list:
            wrapped.append("</ul>")
        chapters_html[i] = (h1, wrapped)

    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""

    style_css = """body { font-family: sans-serif; line-height: 1.6; color: #1a1a2e; }
h1 { color: #1a1a2e; border-bottom: 2px solid #4a90d9; padding-bottom: 8px; }
h2 { color: #1a1a2e; margin-top: 24px; }
h3 { color: #333; }
p { margin: 8px 0; }
ul { margin: 8px 0; }
li { margin: 4px 0; }
blockquote { border-left: 4px solid #4a90d9; padding-left: 16px; color: #666; margin: 16px 0; }
a { color: #4a90d9; }
@page { margin: 2cm; }"""

    opf_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    opf_parts.append('<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">')
    opf_parts.append('<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">')
    opf_parts.append(f'<dc:title>{esc(title)}</dc:title>')
    opf_parts.append(f'<dc:language>{lang}</dc:language>')
    opf_parts.append('<dc:creator>AIIA-NTBLM-Factory v1.0</dc:creator>')
    opf_parts.append('</metadata>')
    opf_parts.append('<manifest>')
    opf_parts.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
    opf_parts.append('<item id="style" href="style.css" media-type="text/css"/>')
    for i, (h1, _) in enumerate(chapters_html):
        ch_id = f"ch{i+1:02d}"
        ch_file = f"ch{i+1:02d}.xhtml"
        opf_parts.append(f'<item id="{ch_id}" href="{ch_file}" media-type="application/xhtml+xml"/>')
    opf_parts.append('</manifest>')
    opf_parts.append('<spine>')
    opf_parts.append('<itemref idref="ncx"/>')
    for i in range(len(chapters_html)):
        opf_parts.append(f'<itemref idref="ch{i+1:02d}"/>')
    opf_parts.append('</spine>')
    opf_parts.append('</package>')

    ncx_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    ncx_parts.append('<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">')
    ncx_parts.append(f'<docTitle><text>{esc(title)}</text></docTitle>')
    ncx_parts.append('<docAuthor>AIIA-NTBLM-Factory v1.0</docAuthor>')
    ncx_parts.append('<navMap>')
    for i, (h1, _) in enumerate(chapters_html):
        ncx_parts.append(f'<navPoint id="nav{i+1}" playOrder="{i+1}">')
        ncx_parts.append(f'<navLabel><text>{esc(h1)}</text></navLabel>')
        ncx_parts.append(f'<content src="ch{i+1:02d}.xhtml"/>')
        ncx_parts.append('</navPoint>')
    ncx_parts.append('</navMap>')
    ncx_parts.append('</ncx>')

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("META-INF/container.xml", container_xml)
        zf.writestr("OEBPS/style.css", style_css)
        zf.writestr("OEBPS/content.opf", "\n".join(opf_parts))
        zf.writestr("OEBPS/toc.ncx", "\n".join(ncx_parts))
        for i, (h1, content) in enumerate(chapters_html):
            ch_html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{esc(h1)}</title><meta charset="UTF-8"/></head>
<body>
<h1>{esc(h1)}</h1>
{"".join(content)}
</body>
</html>"""
            zf.writestr(f"OEBPS/ch{i+1:02d}.xhtml", ch_html)

    if output_path.stat().st_size > 500:
        print(f"  ePub generado: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")
        return str(output_path)
    else:
        print("  Error generando ePub")
        return ""


def check_pdf_metadata(pdf_path: str) -> Dict:
    """Check PDF metadata and basic validity."""
    p = Path(pdf_path)
    if not p.exists():
        return {"valid": False, "error": "File not found"}
    size_kb = p.stat().st_size / 1024
    is_pdf = p.read_bytes()[:5] == b"%PDF-"
    return {
        "valid": is_pdf and size_kb > 10,
        "size_kb": round(size_kb, 1),
        "filename": p.name,
        "pages": "unknown",
    }


if __name__ == "__main__":
    print("=== PDF Designer Test ===")
    sample = """# Documento de Prueba

## Introduccion
Este es un documento de prueba del sistema AIIA-NTBLM-Factory.

## Contenido Principal
- Idea 1: Contenido importante
- Idea 2: Otro concepto clave
- Idea 3: Tema relevante

## Conclusión
El documento de prueba funciona correctamente.
"""
    print("\n  Probando PDF desktop...")
    result = generate_pdf(sample, None, "es", "desktop")
    print(f"    OK: {result}" if result else "    FAIL: no se genero PDF")

    print("\n  Probando ePub...")
    epub = generate_epub(sample, "es")
    print(f"    OK: {epub}" if epub else "    FAIL: no se genero ePub")
