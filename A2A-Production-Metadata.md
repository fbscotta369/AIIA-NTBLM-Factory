# A2A Production Metadata

> System metadata for production operations of AIIA-NTBLM-Factory.
> Updated: 2026-08-21. All times UTC-3.

---

## System Identity

- **Name**: AIIA-NTBLM-Factory v1.0
- **Description**: NotebookLM-powered digital product factory — generates sellable PDFs, ePub, audio, video, quiz from YouTube sources + NotebookLM deep analysis
- **Owner**: AIIA Labs family
- **Owner GitHub**: fbscotta369
- **Google Account**: fbscotta@gmail.com
- **Repo**: https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
- **Domain**: Digital product manufacturing (e-books, audio books, video courses, quizzes)

---

## Architecture

- **Model**: A→B→Z linear pipeline with 6 phases
- **Phases**:
  1. Source Collection (YouTube Data API)
  2. NotebookLM Deep Analysis (browser automation via Playwright)
  3. Content Generation (docs, slides, infographics, audio, video, quiz — bilingual)
  4. PDF Design (desktop + mobile + ePub)
  5. Quality Control (6-point verification)
  6. Export (bundle ready to sell)

- **Languages**: Spanish (Latin American) + English (British)
- **Voice**: Female voices for both languages (ElevenLabs)
- **Source Material**: YouTube videos (Dan Martell channel + related topics)

---

## Environment

- **Runtime**: Python 3.11+
- **Browser Automation**: Playwright (Chromium)
- **TTS**: ElevenLabs API
- **LLM**: OpenRouter (for content generation)
- **PDF Engine**: LaTeX (texlive)
- **Video Engine**: FFmpeg (+ Manim optional)
- **ePub Engine**: pandoc (+ ebooklib fallback)

---

## Dependencies (latest versions)

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Runtime |
| playwright | latest | Browser automation |
| elevenlabs | latest | TTS |
| openai / openrouter-client | latest | LLM content generation |
| google-api-python-client | latest | YouTube search |
| pydub | latest | Audio processing |
| texlive | system | PDF generation |
| ffmpeg | system | Video |
| pandoc | system | ePub |

---

## External Services / APIs

| Service | API Key Env Var | Free/Paid | Purpose |
|---------|----------------|-----------|---------|
| YouTube Data API v3 | YOUTUBE_API_KEY | Free (10k units/day) | Video search |
| NotebookLM | (Browser auth, no API key) | Free | Deep analysis |
| ElevenLabs | ELEVENLABS_API_KEY | Paid (Starter $5/mo min for commercial) | TTS |
| OpenRouter | OPENROUTER_API_KEY | Paid/Free tier | LLM content generation |

---

## Credentials / Secrets

- **Google login (NotebookLM)**: Handle via browser cookie session — do NOT store password in env. Use app-password if 2FA enabled.
- **YouTube API key**: Store in env var YOUTUBE_API_KEY
- **ElevenLabs API key**: Store in env var ELEVENLABS_API_KEY
- **OpenRouter API key**: Store in env var OPENROUTER_API_KEY

**DO NOT commit real credentials to repo**. Use .env (gitignored) for local, secrets manager or env injection for CI/CD.

---

## Output Structure

```
output/
├── <topic_slug>/
│   ├── pdf_desktop/
│   │   ├── ES_<slug>_desktop.pdf
│   │   └── EN_<slug>_desktop.pdf
│   ├── pdf_mobile/
│   │   ├── ES_<slug>_mobile.pdf
│   │   └── EN_<slug>_mobile.pdf
│   ├── epub/
│   │   ├── ES_<slug>.epub
│   │   └── EN_<slug>.epub
│   ├── audio/
│   │   ├── ES_<slug>.mp3
│   │   └── EN_<slug>.mp3
│   ├── video/
│   │   ├── ES_<slug>.mp4
│   │   └── EN_<slug>.mp4
│   ├── quiz/
│   │   ├── ES_<slug>_quiz.md
│   │   └── EN_<slug>_quiz.md
│   └── metadata.json
```

---

## Version Tracking

- **A2A files**: Updated at every agent session start. Source of truth for system state.
- **Code version**: Tracked via Git commits. Tags: v1.0, v1.1, etc.
- **Product version**: metadata.json in each output/<topic>/ directory

---

## Health / Monitoring

- **Pipeline health**: Check after each run — all phases pass? Quality checks all green?
- **External dependency health**: Monitor API quotas, auth sessions, voice availability
- **Budget tracking**: ElevenLabs character count, OpenRouter token usage

---

## Rollback / Recovery

- **Source collection failure**: Retry with different query, or manual URL input
- **NotebookLM failure**: Re-login, use saved browser cookies, retry
- **Content generation failure**: Regenerate specific missing content
- **PDF failure**: Fix LaTeX errors, re-render
- **Quality check failure**: Fix identified issues, re-check

---

## Stakeholders

- **AIIA Labs family**: System owners, maintainers
- **FB (fbscotta@gmail.com)**: Google account owner, content subject authority (Dan Martell knowledge)
- **OpenRouter**: LLM provider
- **ElevenLabs**: TTS provider
- **Google**: NotebookLM platform + YouTube data

---

## Support / Escalation

- **Technical issues**: Check A2A-Blockers.md + A2A-Bugs.md
- **Auth issues**: BLO-01, BLO-07
- **API quota issues**: BLO-02
- **Commercial issues**: BLO-03 (ElevenLabs paid plan)

---

> Updated: 2026-08-21. Next review: after first successful pipeline run.
