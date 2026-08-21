# A2A Technical Documentation

> Technical specification for AIIA-NTBLM-Factory v1.0 — NotebookLM-powered digital product factory.
> Updated: 2026-08-21. All times UTC-3.

---

## System Overview

AIIA-NTBLM-Factory takes a topic (e.g., "Como auto educarse con IA. El método Dan Martell"), finds relevant YouTube videos, sends them to NotebookLM for deep analysis (summary, slides, FAQ, timeline), then generates a full suite of sellable digital products: PDF (desktop + mobile), ePub, audio (MP3), video (MP4), and quiz.

**Bilingual output**: Spanish (Latin American, Female voice) and English (British, Female voice).

**Sellable formats**: Amazon KDP, Shopify, Hotmart — ready to list.

---

## Architecture: A→B→Z

```
A: Input Topic
   │
   ▼
B: Source Collection (YouTube Data API + fallback)
   │
   ▼
   NotebookLM Deep Analysis (browser automation → login → create notebook → add sources → extract)
   │
   ▼
   Content Generation (docs, slides, infographics, audio, video, quiz)
   │
   ▼
   PDF Design (desktop + mobile + ePub)
   │
   ▼
   Quality Control (6-point check)
   │
   ▼
Z: Export (output/<topic>/ all files ready to sell)
```

---

## Components

### 1. factory.py — Orchestrator

Main entry point. Coordinates phases, manages env, handles retries.

```bash
python factory.py --topic "Como auto educarse con IA. El método Dan Martell" --lang all
```

### 2. notebooklm_client.py — Browser Automation

Uses Playwright to:
1. Login to Google account (fbscotta@gmail.com)
2. Navigate to notebooklm.google.com
3. Create a new notebook
4. Add YouTube URLs as sources
5. Wait for analysis to generate
6. Extract: summary, slides, FAQ, timeline

**Critical**: NotebookLM has no public API. Must use browser UI automation.

### 3. content_generator.py — Multi-Format Generation

Takes NotebookLM analysis JSON and generates:

| Format | Tool | Output |
|--------|------|--------|
| Docs (MD) | OpenRouter LLM | Markdown |
| Slides | Mermaid + SVG | diagrams |
| Infographics | Mermaid/Airtable-style | SVG |
| Audio | ElevenLabs TTS | MP3 (female voice) |
| Video | Manim/p5/FFmpeg | MP4 |
| Quiz | LLM from content | JSON/MD |

### 4. pdf_designer.py — PDF + ePub Generation

Takes docs + slides + infographics and produces:

- **Desktop PDF**: LaTeX-generated, A4, professional layout with cover page
- **Mobile PDF**: Condensed, phone-readable
- **ePub**: Generated via pandoc or similar

### 5. quality_checker.py — 6-Point Verification

1. **Completeness** — PDF has intro + body + conclusion + appendix
2. **Coherence** — Sections flow logically, no contradictions
3. **Visual quality** — Infographics are referenced and load correctly
4. **Audio quality** — MP3 length matches expected narration time
5. **Mobile-friendly** — PDF readable on small screens
6. **Branding consistency** — Style, colors, fonts consistent

---

## Data Flow

```
Topic → YouTube search → URLs [{title, url, channel}]
     → NotebookLM (browser auto) → analysis JSON {summary, slides, faq, timeline}

analysis JSON → content_generator → {
   docs_md,
   slides SVG,
   infographics SVG,
   audio_mp3,
   video_mp4,
   quiz_json
}

docs + slides + infographics → pdf_designer → {
   pdf_desktop,
   pdf_mobile,
   epub
}

All outputs → quality_checker → pass/fail

Pass → export to output/<topic>/
```

---

## Environment Variables

```bash
# Authentication (for browser automation)
# Store Google session cookies, not raw password
# For notebooklm_client.py: use playwright's cookie management

# APIs
YOUTUBE_API_KEY=         # YouTube Data API (free tier)
ELEVENLABS_API_KEY=      # ElevenLabs TTS
OPENROUTER_API_KEY=      # LLM access for content generation
```

---

## Voice Configuration

| Language | Voice | Provider |
|----------|-------|----------|
| ES LatAm | Female, Mexican/Argentine accent | ElevenLabs |
| EN British | Female, RP/BBC accent | ElevenLabs |

Voice IDs are stored in config.product.json per product.

---

## Dependencies

| Package | Purpose | Install |
|---------|---------|---------|
| playwright | Browser automation | pip install playwright + install browsers |
| elevenlabs | TTS | pip install elevenlabs |
| openai / openrouter | LLM for content | pip install openai (or openrouter client) |
| google-api-python-client | YouTube search | pip install google-api-python-client |
| pydub | Audio manipulation | pip install pydub |
| mermaid | Diagrams | JS library (node) or mermaid-cli |
| LaTeX (texlive) | PDF generation | System install |
| pandoc | ePub | System install |
| ffmpeg | Video | System install |

---

## Security Notes

- Do NOT store Google password in plain text. Use browser cookie session or browserless auth.
- YouTube API key: rate-limited, use fallback search.
- ElevenLabs: commercial use requires proper API plan.
- All outputs are generated from YouTube sources — copyright must be cleared for commercial sale.

---

## Rollback Notes

If any phase fails:
- Source collection: retry with different query
- NotebookLM: re-login, different browser context
- Content generation: regenerate specific missing part
- PDF: re-render with adjusted LaTeX template
- Quality check: fix issues manually and re-check

---

> Owner: AIIA, updated 2026-08-21
