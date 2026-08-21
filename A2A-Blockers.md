# A2A Blockers — Bloqueos conocidos

> Bloqueos que impiden el avance del sistema.
> Updated: 2026-08-21. All times UTC-3.

---

## Blockers Activos

### 🔴 BLO-01: Playwright con Google login (2FA)
- **Severity**: Critical
- **Swarm**: NotebookLM Client (B)
- **Blocked by**: Google 2FA requires manual verification or app-password
- **Impact**: Cannot automate NotebookLM login without 2FA bypass
- **Workaround available**:
  - Use app-password (Google allows app-specific passwords)
  - Use browser session cookies (pre-login once, save cookies, reuse)
  - Manual one-time login, then persist session
- **Status**: Unblocked (workarounds identified, not yet tested)

### 🔴 BLO-02: YouTube Data API quota
- **Severity**: Medium
- **Swarm**: Source Collection (A)
- **Blocked by**: API quota limits (typically 10,000 units/day for free tier)
- **Impact**: Cannot search many videos per day
- **Workaround**:
  - Cache search results in output/
  - Use alternative: manual search + URL paste
  - Use free tier wisely — search only once per topic
- **Status**: Unblocked (single search per topic is acceptable)

### 🔴 BLO-03: ElevenLabs API key + commercial rights
- **Severity**: High
- **Swarm**: Content Generation (C)
- **Blocked by**: Need paid ElevenLabs plan for commercial use of generated audio
- **Impact**: Cannot generate commercial-quality audio without paid plan
- **Workaround**:
  - Free tier available for testing (non-commercial)
  - For commercial use: need ElevenLabs Starter ($5/mo) or Creator plan
  - Alternative TTS: Google Cloud TTS, Amazon Polly (but ElevenLabs is preferred for female voices + LatAm/UK accents)
- **Status**: Blocked by business decision (need paid plan)

### 🟡 BLO-04: LaTeX installation (PDF generation)
- **Severity**: Medium
- **Swarm**: PDF Design (D)
- **Blocked by**: texlive not installed in this environment
- **Impact**: Cannot generate professional PDF
- **Workaround**:
  - Install texlive: `sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended`
  - Alternative: use Python-based PDF (reportlab, weasyprint — less professional than LaTeX)
- **Status**: Unblocked (installable, not yet installed)

### 🟡 BLO-05: Video generation dependencies
- **Severity**: Medium
- **Swarm**: Content Generation (C)
- **Blocked by**: FFmpeg not installed; Manim needs ffmpeg + latex
- **Impact**: Cannot generate video products
- **Workaround**:
  - Install ffmpeg: `sudo apt-get install ffmpeg`
  - Use simpler video: slides exported as images + audio → ffmpeg concat
  - Alternative: Manim for advanced animations (needs LaTeX + ffmpeg)
- **Status**: Unblocked (installable)

### 🟡 BLO-06: ePub generation
- **Severity**: Low
- **Swarm**: PDF Design (D)
- **Blocked by**: pandoc not installed in this environment
- **Impact**: Cannot generate ePub output
- **Workaround**:
  - Install pandoc: `sudo apt-get install pandoc`
  - Alternative: manual ePub from HTML using ebooklib
- **Status**: Unblocked (installable)

### 🔴 BLO-07: NotebookLM login session persistence
- **Severity**: High
- **Swarm**: NotebookLM Client (B)
- **Blocked by**: Browser automation session is ephemeral across runs
- **Impact**: Must re-login every time, which is slow + may trigger 2FA
- **Workaround**:
  - Save browser cookies between runs (playwright context can be saved/reloaded)
  - Use chromium persistent context: `browser.new_context(storage_state="cookies.json")`
- **Status**: Workaround identified, not yet tested

---

## Already-Handled Blockers

| Id | Issue | Resolution |
|----|-------|------------|
| BKL-OLD-1 | No A2A files | All A2A files created |
| BKL-OLD-2 | No Google API key identified | Identified + ready to use |
| BKL-OLD-3 | No directory structure | Factory structure created |

---

## Resolution Plan

Priority order for unblocking (by severity):

1. **BLO-03** (ElevenLabs paid plan) — business decision, owner action needed
2. **BLO-01 / BLO-07** (2FA + session persistence) — test app-password approach first
3. **BLO-02** (API quota) — not blocking for single-topic test
4. **BLO-04 / BLO-05 / BLO-06** (system deps) — install via apt

---

> Updated: 2026-08-21. Next review: after first NotebookLM login attempt.
