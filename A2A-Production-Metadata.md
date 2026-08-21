# A2A Production Metadata

> System metadata for production operations of AIIA-NTBLM-Factory.
> Updated: 2026-08-21. All times UTC-3. Status: INFRAESTRUCTURA COMPLETA

---

## System Identity

- **Name:** AIIA-NTBLM-Factory v1.0
- **Description:** NotebookLM-powered digital product factory — genera productos digitales vendibles (PDFs, ePub, audio, video, quiz) a partir de videos de YouTube + NotebookLM deep analysis via browser automation
- **Owner:** AIIA Labs family
- **Owner GitHub:** fbscotta369
- **Google Account:** fbscotta@gmail.com
- **Repo:** https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
- **Branch:** main (seguro, commits: 842c374 + 30c0914)
- **Domain:** Digital product manufacturing (e-books, audio books, video courses, quizzes)

---

## Architecture

- **Model:** A→B→Z linear pipeline con 6 fases
- **Fases:**
  1. Source Collection (YouTube Data API v3)
  2. NotebookLM Deep Analysis (browser automation — Playwright)
  3. Content Generation (docs, slides, infographics, audio, video, quiz — bilingüe ES/EN)
  4. PDF Design (desktop PDF + mobile PDF + ePub)
  5. Quality Control (6-point verification automática, ninguna omitida)
  6. Export (bundle listo para vender)

- **Languages:** Spanish (Latin American) + English (British)
- **Voice:** Female voices para ambos idiomas (ElevenLabs TTS)
- **Source Material:** YouTube videos (buscados con YouTube Data API v3)

---

## Environment

- **Runtime:** Python 3.11+
- **Browser Automation:** Playwright (Chromium) — instalado + descargado
- **TTS:** ElevenLabs API (requiere API key + plan de pago para comercial)
- **LLM:** OpenRouter (para generación de contenido — requiere API key)
- **PDF Engine:** reportlab (fallback, funciona sin deps del sistema) + pandoc/LaTeX (opcional, mejor calidad)
- **Video Engine:** FFmpeg (requerido para video)
- **ePub Engine:** pandoc (requerido para ePub)

---

## Dependencies (versión real verificada)

| Dependency | Version | Purpose | Status |
|-----------|---------|---------|--------|
| Python | 3.11+ | Runtime | ✅ OK |
| playwright | latest | Browser automation | ✅ Instalado |
| chromium (Playwright) | v151.0.7922.34 | Browser | ✅ Descargado |
| elevenlabs | latest | TTS | 🔴 Requiere API key |
| openai / openrouter-client | latest | LLM content generation | 🔴 Requiere API key |
| google-api-python-client | latest | YouTube search | 🔴 Requiere API key |
| pydub | latest | Audio manipulation | ⏳ Opcional |
| reportlab | latest | PDF generation (fallback) | ✅ Instalado + probado |
| Pillow | latest | Image generation | ⏳ Opcional |
| matplotlib | latest | Slide image generation | ⏳ Opcional |
| ffmpeg | system | Video composition | ⏳ Requerido (instalar con apt) |
| pandoc | system | ePub + pandoc PDF | ⏳ Opcional |
| texlive-latex-base | system | LaTeX PDF (mejor calidad) | ⏳ Opcional |
| wkhtmltopdf | system | HTML→PDF | ⏳ Opcional |
| weasyprint | system | HTML→PDF | ⏳ Opcional |

---

## External Services / APIs

| Service | API Key Env Var | Free/Paid | Purpose | Status |
|---------|----------------|-----------|---------|--------|
| YouTube Data API v3 | YOUTUBE_API_KEY | Free (10k units/día) | Video search | 🔴 Pendiente key |
| NotebookLM | (Browser auth, sin API key) | Free | Deep analysis | 🔴 Pendiente credenciales |
| ElevenLabs | ELEVENLABS_API_KEY | Paid (Starter $5/mo min para comercial) | TTS | 🔴 Pendiente key |
| OpenRouter | OPENROUTER_API_KEY | Paid/Free tier | LLM content | 🔴 Pendiente key |

---

## Credentials / Secrets

### Google / NotebookLM
- **NOTEBOOKLM_EMAIL:** fbscotta@gmail.com (default)
- **NOTEBOOKLM_PASSWORD:** [REDACTED] — NO usar si 2FA activado, usar app-password
- **NOTEBOOKLM_APP_PASSWORD:** [REDACTED] — RECOMENDADO si 2FA activado
- **GOOGLE_SESSION_COOKIE:** [REDACTED] — base64-encoded cookies de sesión, opcional (más confiable que password)

### APIs
- **YOUTUBE_API_KEY:** [REDACTED] — requerida para YouTube search
- **ELEVENLABS_API_KEY:** [REDACTED] — requerida para TTS
- **OPENROUTER_API_KEY:** [REDACTED] — requerida para LLM content

**DO NOT commit real credentials to repo.** Use .env (gitignored) for local, secrets manager o env injection para CI/CD.

---

## Output Structure

```
output/
└── <topic_slug>/
    ├── pdf_desktop/
    │   └── <lang>_<slug>_desktop.pdf     (A4, professional)
    ├── pdf_mobile/
    │   └── <lang>_<slug>_mobile.pdf      (A5, phone-readable)
    ├── epub/
    │   └── <lang>_<slug>.epub            (reflowable e-book)
    ├── audio/
    │   └── <lang>_<slug>.mp3             (ElevenLabs TTS narration)
    ├── video/
    │   └── <lang>_<slug>.mp4             (FFmpeg slides + audio)
    ├── quiz/
    │   └── <lang>_<slug>_quiz.md         (comprehension questions)
    └── metadata.json                      (version, date, quality results)
```

Ejemplo: `output/como_auto_educarse_con_ia_el_metodo_dan_martell/`

---

## Quality Checks (6 — none skipped)

| # | Check | Severity | What it verifies |
|---|-------|----------|------------------|
| 1 | completeness | CRITICAL | PDF tiene intro + body + conclusion + appendix, size > 50KB |
| 2 | coherence | HIGH | Sections en orden lógico (intro antes de conclusion), contenido > 200 chars |
| 3 | visual_quality | HIGH | Infografías SVG válidas, PDF size > 50KB (contenido visual presente) |
| 4 | audio_quality | MEDIUM | Audio MP3 existe, duration > 30s, size > 5KB |
| 5 | mobile_responsiveness | MEDIUM | Mobile PDF existe, size > 50KB, tamaño < desktop |
| 6 | branding_consistency | LOW | Marca AIIA en docs, color #1a1a2e en SVGs |

---

## Version Tracking

- **A2A files:** Actualizados al inicio de cada sesión + después de cada cambio relevante. Fuente de verdad del sistema.
- **Code version:** Git commits. Tags: v1.0, v1.1, etc.
- **Product version:** metadata.json en cada output/<topic>/ directory

---

## Health / Monitoring

- **Pipeline health:** Verificar después de cada ejecución — todas las fases pasaron? Quality checks todas green?
- **External dependency health:** Monitorear API quotas, auth sessions, voice availability
- **Budget tracking:** ElevenLabs character count, OpenRouter token usage, YouTube API quota

---

## Rollback / Recovery

- **Source collection failure:** Retry con diferente query, o input manual de URLs
- **NotebookLM failure:** Re-login con diferente browser context, o usar cookies guardadas
- **Content generation failure:** Regenerar parte específica faltante
- **PDF failure:** Re-render con template ajustado, o usar reportlab fallback
- **Quality check failure:** Arreglar issues identificados, re-check

---

## Stakeholders

- **AIIA Labs family:** System owners, maintainers
- **FB (fbscotta@gmail.com):** Google account owner, content subject authority (Dan Martell knowledge)
- **OpenRouter:** LLM provider
- **ElevenLabs:** TTS provider
- **Google:** NotebookLM platform + YouTube data

---

## GitHub Status

- **Repo:** https://github.com/fbscotta369/AIIA-NTBLM-Factory
- **Branch:** main
- **Commits:** 2 (842c374 + 30c0914)
- **Files:** 25 archivos (código + docs + config)
- **Push:** ✅ Completed — origin/main actualizado

---

## Soporte / Escalación

- **Issues técnicos:** Revisar A2A-Blockers.md + A2A-Bugs.md
- **Auth issues:** BLO-01 (NotebookLM credentials)
- **API quota issues:** BLO-02, BLO-03
- **Commercial issues:** BLO-02 (ElevenLabs plan de pago requerido)

---

## Estado final del sistema (2026-08-21)

**INFRAESTRUCTURA COMPLETA ✅**

- ✅ 11 archivos A2A documentados y actualizados
- ✅ factory.py — orchestrator A→B→Z con 6 fases
- ✅ config.py + config.product.json — configuración completa
- ✅ lib/ — 5 módulos completos y probados
- ✅ Playwright instalado + Chromium descargado
- ✅ Content Generator: 4/5 funciones probadas OK
- ✅ PDF Designer: reportlab funciona como fallback
- ✅ Quality Checker: 6 checks probados
- ✅ GitHub: 2 commits, 25 archivos, push completado

**PENDIENTE PARA EJECUCIÓN COMPLETA:**
- 🔴 4 credenciales requeridas: YOUTUBE_API_KEY, ELEVENLABS_API_KEY, OPENROUTER_API_KEY, NOTEBOOKLM credenciales (app-password o cookies de sesión)

**Próximo paso:** FB configura credenciales en .env, ejecuta `factory.py --topic "Como auto educarse con IA. El método Dan Martell" --lang all --verify`

---

> Updated: 2026-08-21. Status: INFRAESTRUCTURA COMPLETA. Next review: after first production pipeline run.
