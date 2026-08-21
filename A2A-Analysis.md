# A2A Analysis — A→B→Z Final System Analysis

> Analysis of AIIA-NTBLM-Factory v1.0 from source collection to production-ready product export.
> Updated: 2026-08-21. All times UTC-3.

---

## A→B→Z Lifecycle Overview

### What We're Solving
Given a topic (e.g. "Como auto educarse con IA. El método Dan Martell"), produce a sellable digital product in two languages (ES LatAm/female + EN British/female) from NotebookLM deep analysis.

### Why This Matters
NotebookLM provides structured analysis of YouTube sources (summaries, slides, FAQ, timeline). We use it as the engine, then package the output as professional digital products: PDF (desktop + mobile), ePub, audio (MP3), video (MP4), and quiz.

### What We've Done So Far
- ✅ A2A-Quickstart.md completed
- ✅ A2A-WIP.md completed
- ✅ A2A-Tasks.md completed
- 🔴 Todo: 6 remaining A2A files + factory.py + structure

---

## B Analysis — ¿Cómo se compone el sistema y qué agencia usa para qué?

### B1: NotebookLM Client Agent (NotebookLM authentication + source management)
Uses browser automation via Playwright. Cannot directly call NotebookLM APIs — Google has no public API. Must simulate human login + source addition via browser automation.

### B2: Content Generation Agent (Analysis → Docs, Slides, Infographics, Audio, Video, Quiz)
Takes NotebookLM-extracted content and generates:
- Markdown docs from analysis
- Infographics from Mermaid/Airtable-style diagrams
- Audio from ElevenLabs (female voices: ES LatAm + EN British)
- Video from Manim/p5.js/FFmpeg
- Quiz from analysis content

### B3: Quality Checker Agent (6 verifications)
Runs 6-point automated verification before export. Each check is pass/fail with a clear reason.

### B4: Orchestrator Agent (factory.py)
Coordinates all phases. Manages environment, calls each sub-agent in sequence, handles errors, retries on transient failures.

---

## B2: Architecture Detail

```
Flow (A→B→Z):
A. Input:
   - Topic string (e.g., "Como auto educarse con IA. El método Dan Martell")
   - Language: "es" or "en" or "all" (both)
   - Voice: "female" or "male"

B. Processing:
   Phase 1: Source Collection
     → Search YouTube for related videos (Dan Martell channel + related topics)
     → Collect URLs + metadata

   Phase 2: NotebookLM Analysis
     → Login to notebooklm.google.com
     → Create notebook
     → Add sources (YouTube URLs)
     → Extract analysis: summary, slides, FAQ, timeline, timeline
     → Save raw analysis JSON

   Phase 3: Content Generation
     → Generate docs (markdown) from analysis
     → Generate infographics (SVG/Mermaid) from key concepts
     → Generate audio (MP3, ElevenLabs) — ES + EN versions
     → Generate video (MP4) — slides + narration
     → Generate quiz (questions + answers)

   Phase 4: PDF Design
     → Combine docs + slides + infographics into PDF
     → Desktop: A4/letter size, professional layout
     → Mobile: condensed layout, readable on phones
     → ePub: reflowable e-book format

   Phase 5: Quality Control (6 checks)
     1. Completeness — all sections present
     2. Coherence — narrative flow logical
     3. Visual quality — infographics sharp
     4. Audio quality — playback length reasonable
     5. Mobile-friendly — PDF readable in small screen
     6. Branding consistency — style uniform

   Phase 6: Export
     → Bundle into output/<topic_slug>/
     → Git commit + push (if configured)

C. Output:
   PDF (desktop + mobile), ePub, audio MP3, video MP4, quiz
   Two versions: ES (LatAm/female) + EN (British/female)
```

---

## C Analysis — Infrastructure & Dependencies

### Required APIs / Services
| Service | Purpose | Env Var | Cost |
|---------|---------|---------|------|
| Google API | YouTube search | GOOGLE_API_KEY | Free tier |
| NotebookLM | Deep analysis | Browser auth (NOT EB key) | Free |
| ElevenLabs | TTS (female voices) | ELEVENLABS_API_KEY | Paid ($5+/mo) |
| PDF generation | LaTeX → PDF | System install (texlive) | Free |
| Video generation | FFmpeg + Manim | System install | Free |

### Local Dependencies
- Python 3.11+
- pip packages: playwright, pydub, elevenlabs
- System: texlive-latex-base (or mupdf), ffmpeg, pandoc (for ePub)

### Directory Structure

```
AIIA-NTBLM-Factory/
├── A2A-*.md                  # All handoff files
├── factory.py                # Orchestrator
├── config.product.json       # Product config (title, topic, voice, lang, sources)
├── .env.example              # Template credentials
├── .gitignore
├── requirements.txt
├── output/                   # Generated products (gitignored)
│   └── <topic-slug>/
├── lib/                      # Internal modules
│   ├── notebooklm_client.py
│   ├── content_generator.py
│   └── quality_checker.py
├── tests/
│   └── test_pipeline.py
└── assets/                   # Static assets (logos, templates)
```

---

## D: Environment Variables Required

```bash
GOOGLE_API_KEY=AIza...
ELEVENLABS_API_KEY=elevenlab_xxx
# NOTEBOOKLM authentication uses browser session cookies
# DO NOT put Google password here — use browser automation
# Set language preferences:
LANGUAGE_PREFERENCE=en  # or es
VOICE_GENDER=female
```

---

## Already-Handled Issues

1. **Video downloads for NotebookLM upload** — Google automatically transcribes YouTube videos, no download needed. URLs suffice.
2. **Brand consistency** — handled by LaTeX template + ElevenLabs voice selection.
3. **Version tracking** — A2A files are the source of truth, updated at each session start.

---

## Uncovered / Future Work

1. **Direct YouTube transcript extraction** — currently relying on NotebookLM's auto-transcription. Alternative: youtube-transcript API as fallback.
2. **Quiz content type** — currently text-based. Future: interactive HTML quiz.
3. **Multi-file ePub generation** — one ePub per language. Currently single combined.

---

## Owner Notes

This is a Phase 1 implementation. Missing: actual pipeline code, Authentication flow testing, + production deployment configs (Vercel, Supabase).

---

> Updated: 2026-08-21
> Next review: when first end-to-end test runs
