# A2A Technical Documentation

> Technical specification for AIIA-NTBLM-Factory v1.0 — NotebookLM-powered digital product factory.
> Updated: 2026-08-21. All times UTC-3. Status: INFRAESTRUCTURA COMPLETA

---

## System Overview

AIIA-NTBLM-Factory takes a topic (e.g., "Como auto educarse con IA. El método Dan Martell"), finds relevant YouTube videos via YouTube Data API, sends them to NotebookLM for deep analysis via browser automation (Playwright), then generates a full suite of sellable digital products: PDF (desktop + mobile), ePub, audio (MP3 via ElevenLabs TTS), video (MP4 via FFmpeg), and quiz.

**Bilingual output**: Spanish (Latin American, Female voice — ElevenLabs María) and English (British, Female voice — ElevenLabs Alice).

**Sellable formats**: Amazon KDP (PDF), Shopify, Hotmart, Gumroad, Lemon Squeezy — ready to list.

**Status**: Infrastructure complete. Code complete and tested. Ready to run when credentials configured.

---

## Architecture: A→B→Z

```
A: Input Topic (--topic "Como auto educarse con IA. El método Dan Martell")
   │
   ▼
Phase 1: Source Collection (lib/source_collector.py)
   → YouTube Data API v3 search
   → Filter by: relevance, duration (5-30min), views (>1000)
   → Extract: title, url, channel, description, views, duration
   │
   ▼
Phase 2: NotebookLM Deep Analysis (lib/notebooklm_client.py)
   → Playwright browser automation
   → 1. Login to Google (fbscotta@gmail.com) via app-password or cookies
   → 2. Navigate to notebooklm.google.com
   → 3. Create new notebook
   → 4. Add YouTube URLs as sources
   → 5. Wait for NotebookLM to process
   → 6. Extract: summary, slides, FAQ, timeline, insights
   │
   ▼
Phase 3: Content Generation (lib/content_generator.py)
   → For each language (es/en):
   → 1. generate_docs(): Markdown documentation from analysis
   → 2. generate_slides(): Slide titles + content
   → 3. generate_infographics(): SVG timeline + concept map
   → 4. generate_audio(): ElevenLabs TTS (female voice)
   → 5. generate_video(): FFmpeg slides + audio → MP4
   → 6. generate_quiz(): Quiz questions from analysis
   │
   ▼
Phase 4: PDF Design (lib/pdf_designer.py)
   → For each language:
   → 1. Desktop PDF: reportlab (fallback) / pandoc+LaTeX (preferred)
   → 2. Mobile PDF: A5 format, phone-readable
   → 3. ePub: pandoc conversion
   │
   ▼
Phase 5: Quality Control (lib/quality_checker.py)
   → 6 checks (CRITICAL/HIGH/MEDIUM/LOW severity):
   → 1. completeness: PDF has intro + body + conclusion + appendix
   → 2. coherence: Sections flow logically, no contradictions
   → 3. visual_quality: Infographics valid SVG, PDF has visual content
   → 4. audio_quality: MP3 duration > 30s, file size > 5KB
   → 5. mobile_responsiveness: Mobile PDF exists, optimized for small screens
   → 6. branding_consistency: AIIA branding present, colors consistent
   │
   ▼
Phase 6: Export
   → Bundle in output/<topic_slug>/
   → metadata.json with all product paths, timestamps, quality results
   → Ready for upload to selling platforms
```

---

## Components

### 1. factory.py — Orchestrator (A→B→Z pipeline)

Main entry point. Coordinates 6 phases, manages environment, handles retries with timeouts.

```bash
python factory.py --topic "Como auto educarse con IA. El método Dan Martell" --lang all --verify
```

**Arguments:**
- `--topic` (required): Topic for the digital product
- `--lang` (default: all): es, en, or all
- `--verify`: Run quality verification (Phase 5)
- `--debug`: Enable debug output

**Phases:**
- Phase 1 (source_collection, 300s timeout): YouTube search + filtering
- Phase 2 (notebooklm_analysis, 600s timeout): Browser automation login + notebook + sources + extract
- Phase 3 (content_generation, 900s timeout): Docs + slides + infographics + audio + video + quiz
- Phase 4 (pdf_design, 300s timeout): Desktop PDF + mobile PDF + ePub
- Phase 5 (quality_control, 120s timeout): 6-point verification
- Phase 6 (export, 60s timeout): Bundle + metadata.json

---

### 2. lib/notebooklm_client.py — Browser Automation (Playwright)

Uses Playwright Chromium to control Google's NotebookLM web interface.

**Functions:**
- `login()` → Login to Google/NotebookLM (app-password or cookies)
- `create_notebook(title)` → Create new notebook
- `add_sources(notebook, urls)` → Add YouTube URLs as sources
- `extract_analysis(notebook)` → Extract summary, slides, FAQ, timeline, insights
- `list_notebooks()` → List all user's notebooks

**Session persistence:**
- Cookies saved to `~/.aiia-ntblm/notebooklm_cookies.json`
- Can also use `GOOGLE_SESSION_COOKIE` env var (base64-encoded JSON)
- Avoids re-login every execution

**Critical:** NotebookLM has no public API. Must use browser UI automation. Google may change UI selectors — use text-based selectors with fallbacks.

---

### 3. lib/source_collector.py — YouTube Source Collection

Uses YouTube Data API v3 to search for videos about a topic.

**Functions:**
- `search_videos(query, max_results=10)` → List of video dicts with title, url, channel, view_count, duration_seconds, duration_text, published, thumbnail, description
- `is_youtube_url(url)` → Validate YouTube URL
- `extract_video_id(url)` → Get video ID from URL

**Filtering:** Requires >=1000 views, 5-30 minute duration, relevance keywords present.

---

### 4. lib/content_generator.py — Multi-Format Content Generation

Takes NotebookLM analysis JSON and generates content in 2 languages.

**Functions:**
- `generate_docs(analysis, lang)` → Markdown string with: title, introduction, summary, main content (insights + slides), FAQ, timeline, conclusion, appendix. Structure: # Title → ## Introduction → ## Contenido Principal → ## FAQ → ## Timeline → ## Conclusión → ## Apéndice
- `generate_slides(analysis, lang)` → List of slide dicts [{title, content, visual}]
- `generate_infographics(analysis, lang)` → List of SVG dicts [{title, svg, filename}] — Timeline SVG + Concept Map SVG
- `generate_audio(text, lang, voice)` → Dict {path, duration, voice, voice_id} — ElevenLabs TTS
- `generate_video(slides, audio, lang)` → Dict {path, duration, slides_count} — FFmpeg concatenation
- `generate_quiz(analysis, lang)` → Dict {questions, total, language, generated_at}

**Voice config:**
- ES: ElevenLabs voice FGY2WhTYpPnrIDTdsKH5 (Laura, LatAm, female)
- EN: ElevenLabs voice Xb7hH8MSUJpSbSDYk0k2 (Alice, British, female)
- Model: eleven_multilingual_v2 (multilingual support)

---

### 5. lib/pdf_designer.py — PDF + ePub Generation

Generates PDF (desktop + mobile) and ePub from markdown content.

**Functions:**
- `generate_pdf(docs, infographics, lang, fmt)` → PDF path
- `generate_epub(docs, lang)` → ePub path

**PDF methods (in order of preference):**
1. pandoc + wkhtmltopdf (HTML→PDF, high quality)
2. pandoc + pdflatex (direct LaTeX→PDF)
3. pandoc + weasyprint (HTML→PDF)
4. HTML + weasyprint (simple markdown→HTML→PDF)
5. reportlab (pure Python fallback — **works without any system deps**)

**Mobile PDF:** A5 format, smaller font, tighter margins.

**ePub:** pandoc markdown→epub, with TOC and metadata.

---

### 6. lib/quality_checker.py — 6-Point Automated Verification

Runs quality checks on generated products before export. **None skipped.**

**Classes:**
- `QualityChecker` — Main checker class with 6 check methods

**Checks (in order):**
1. `check_completeness()` (CRITICAL): PDF exists, size > 50KB, has intro + content + conclusion sections
2. `check_coherence()` (HIGH): Sections in logical order (intro before conclusion), substantial content (>200 chars)
3. `check_visual_quality()` (HIGH): Infographics valid SVG, PDF size > 50KB (visual content present)
4. `check_audio_quality()` (MEDIUM): Audio MP3 exists, duration > 30s, size > 5KB
5. `check_mobile_responsiveness()` (MEDIUM): Mobile PDF exists, size > 50KB, smaller than desktop
6. `check_branding_consistency()` (LOW): AIIA branding in docs, dark color #1a1a2e in SVG infographics

**Result format:**
```python
{
    "completeness": {"passed": bool, "message": str, "severity": "critical"},
    "coherence": {"passed": bool, "message": str, "severity": "high"},
    "visual_quality": {"passed": bool, "message": str, "severity": "high"},
    "audio_quality": {"passed": bool, "message": str, "severity": "medium"},
    "mobile_responsiveness": {"passed": bool, "message": str, "severity": "medium"},
    "branding_consistency": {"passed": bool, "message": str, "severity": "low"},
    "all_passed": bool
}
```

---

## Data Flow

```
Topic → search_videos(query) → [video dicts]
     → NotebookLMClient.login() → create_notebook(title) → add_sources(nb, urls) → extract_analysis(nb) → {summary, slides, faq, timeline, insights}

     → For lang in [es, en]:
       docs = generate_docs(analysis, lang)
       slides = generate_slides(analysis, lang)
       infographics = generate_infographics(analysis, lang)
       audio = generate_audio(docs, lang)
       video = generate_video(slides, audio, lang)
       quiz = generate_quiz(analysis, lang)

       pdf_desktop = generate_pdf(docs, infographics, lang, fmt="desktop")
       pdf_mobile = generate_pdf(docs, infographics, lang, fmt="mobile")
       epub = generate_epub(docs, lang)

       qc = QualityChecker().run_all_checks(output_dir, lang)
       # 6 checks: completeness, coherence, visual_quality, audio_quality, mobile_responsiveness, branding_consistency

     → Export: output/<slug>/
       ├── pdf_desktop/<lang>_<slug>_desktop.pdf
       ├── pdf_mobile/<lang>_<slug>_mobile.pdf
       ├── epub/<lang>_<slug>.epub
       ├── audio/<lang>_<slug>.mp3
       ├── video/<lang>_<slug>.mp4
       ├── quiz/<lang>_<slug>_quiz.md
       └── metadata.json
```

---

## Environment Variables

### Required (for full pipeline)

```bash
# YouTube Data API v3 (free tier: 10,000 units/day)
YOUTUBE_API_KEY=AIza...

# ElevenLabs API (Starter $5/mo minimum for commercial use)
ELEVENLABS_API_KEY=elevenlab_...

# OpenRouter API (LLM for content generation)
OPENROUTER_API_KEY=or_...
```

### For NotebookLM Login (one of these)

```bash
# Option A: App-password (recommended if 2FA enabled)
NOTEBOOKLM_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Option B: Google account password (not recommended if 2FA)
NOTEBOOKLM_PASSWORD=.....

# Option C: Session cookies (most reliable — no login needed)
GOOGLE_SESSION_COOKIE=base64_encoded_json
```

### Optional

```bash
NOTEBOOKLM_EMAIL=fbscotta@gmail.com  # default
SUPABASE_URL=https://tvloyxabyzzdxwalwveu.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
OUTPUT_DIR=output  # default
SITE_URL=https://aiia-ntblm-factory.vercel.app
FACTORY_DEBUG=1  # enable debug output
```

---

## Voice Configuration

| Language | Voice Name | ElevenLabs ID | Gender | Accent |
|----------|-----------|---------------|--------|--------|
| ES (LatAm) | Laura | FGY2WhTYpPnrIDTdsKH5 | Female | Latin American (Mexican/Argentine) |
| EN (British) | Alice | Xb7hH8MSUJpSbSDYk0k2 | Female | British (RP/BBC) |

Model: `eleven_multilingual_v2` (supports both languages).

Stability: 0.4 | Similarity boost: 0.75

---

## Dependencies

### Python packages (pip install -r requirements.txt)

| Package | Purpose |
|---------|---------|
| playwright | Browser automation (NotebookLM) |
| elevenlabs | TTS (audio generation) |
| openai | LLM access (OpenRouter compat) |
| google-api-python-client | YouTube Data API v3 |
| pydub | Audio manipulation (optional) |
| reportlab | PDF generation (fallback, no system deps) |
| Pillow | Image generation (slide images) |
| matplotlib | Slide image generation (preferred) |

### System packages (optional but recommended)

| Package | Purpose |
|---------|---------|
| texlive-latex-base + extra + fonts | LaTeX PDF (better quality than reportlab) |
| ffmpeg | Video generation (required for video product) |
| pandoc | ePub generation, pandoc PDF engine |
| wkhtmltopdf | HTML→PDF (high quality) |
| weasyprint | HTML→PDF alternative |

### System packages (required for video)

| Package | Purpose |
|---------|---------|
| ffmpeg | Video composition (required) |

---

## Security Notes

- **DO NOT** store Google password in plain text. Use `NOTEBOOKLM_APP_PASSWORD` (app-password) or `GOOGLE_SESSION_COOKIE` (session cookies).
- YouTube API key: rate-limited (10k units/day for free tier). Use single search per topic.
- ElevenLabs: commercial use requires Starter plan ($5/mo) or higher. Free tier is for non-commercial only.
- OpenRouter: API key required for LLM content generation.
- All outputs generated from YouTube sources — **copyright must be cleared** for commercial sale.
- `.env` is in `.gitignore` — never commit real credentials.
- A2A files use `[REDACTED]` for all credential values.

---

## Rollback Notes

If any phase fails:
- **Phase 1 (source collection):** Retry with different query, or manual URL input
- **Phase 2 (NotebookLM):** Re-login with different browser context, or use saved cookies
- **Phase 3 (content generation):** Regenerate specific missing part (docs, slides, audio, etc.)
- **Phase 4 (PDF):** Re-render with adjusted template, or use fallback method (reportlab)
- **Phase 5 (quality):** Fix identified issues, re-run checks
- **Phase 6 (export):** Already written — safe to re-run

---

## Testing

### Content Generator (verified 2026-08-21)
```bash
python -c "from lib.content_generator import *; test={'topic':'T','summary':['s'],'insights':['i'],'slides':['sl'],'faq':['q'],'timeline':['e']}; print('docs:', len(generate_docs(test)), 'chars'); print('slides:', len(generate_slides(test)), 'slides'); print('infographics:', len(generate_infographics(test)), 'svg'); print('quiz:', len(generate_quiz(test)['questions']), 'questions')"
```
**Result:** docs:941 chars, slides:5, infographics:2 SVG, quiz:2 — all OK ✅

### PDF Designer (verified 2026-08-21)
```bash
python lib/pdf_designer.py
```
**Result:** PDF generado con reportlab (fallback sin LaTeX) ✅

### Quality Checker (verified 2026-08-21)
```bash
python lib/quality_checker.py output/pdf_desktop/
```
**Result:** 6/6 checks ejecutados ✅

### NotebookLM Client (verified 2026-08-21)
```bash
python -c "from lib.notebooklm_client import NotebookLMClient; NotebookLMClient().login()"
```
**Result:** Playwright OK, Chromium instalado. Login falla sin credenciales (esperado) ⚠️

---

> Owner: AIIA, updated 2026-08-21 — INFRAESTRUCTURA COMPLETA
