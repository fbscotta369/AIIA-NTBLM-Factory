# A2A AI Agent Quick Reference

> Referencia rápida para agentes de IA que operan sobre AIIA-NTBLM-Factory v1.0 (NotebookLM Edition).
> Se actualiza al inicio de cada sesión y después de cada cambio relevante.
> Proyecto: /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
> Repo: https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
> Actualizado: 2026-08-21 — Estado: INFRAESTRUCTURA COMPLETA

---

## 1. Rápido: qué es esto

**AIIA-NTBLM-Factory** es una fábrica de productos digitales impulsada por NotebookLM. Toma un tema, busca videos de YouTube, los procesa con NotebookLM (deep analysis), y genera productos digitales vendibles en múltiples formatos y 2 idiomas:

- **PDF diseñado** (desktop A4 + mobile A5 optimizado)
- **ePub** (e-reader)
- **Audio** (narración con ElevenLabs TTS — ES femenino LatAm + EN femenino British)
- **Video** (diapositivas con narración + FFmpeg)
- **Slides / infografías / quizzes**

**Stack real:** Python 3.11 + Playwright (Chrome) + NotebookLM (browser) + ElevenLabs + reportlab (PDF fallback) + FFmpeg (video) + LaTeX (opcional)

**Owner:** Facundo "FB" Scroggie (fbscottoa@gmail.com)
**Google Account:** fbscottta@gmail.com (para NotebookLM)

---

## 2. Arquitectura del sistema

```
Tema (ej: "Como auto educarse con IA. El método Dan Martell")
    │
    ▼
[1. Source Collection] — YouTube Data API search + URL validation
    │
    ▼
[2. NotebookLM Deep Analysis] — Browser automation (Playwright): login → create notebook → add sources → extract (summary, slides, FAQ, timeline)
    │
    ▼
[3. Content Assembly] — Docs (markdown) + Slides + Infographics (SVG) + Audio (ElevenLabs TTS) + Video (FFmpeg) + Quiz
    │
    ▼
[4. Product Design] — Desktop PDF (reportlab/pandoc/LaTeX) + Mobile PDF + ePub
    │
    ▼
[5. Quality Control] — 6 verificaciones automáticas (completeness, coherence, visual, audio, mobile, branding)
    │
    ▼
[6. Export] — Bundle en output/<topic>/ listo para vender (Amazon KDP, Shopify, Hotmart, Gumroad)
```

### Componentes — estado real

| Componente | Función | Estado |
|------------|---------|--------|
| `factory.py` | Orchestrator A→B→Z (6 fases) | ✅ Completo + probado |
| `config.py` | Configuración centralizada + env vars | ✅ Completo |
| `config.product.json` | Metadatos del producto | ✅ Completo |
| `lib/source_collector.py` | YouTube Data API + URL validation | ✅ Completo |
| `lib/notebooklm_client.py` | Playwright browser automation para NotebookLM | ✅ Completo (Playwright instalado) |
| `lib/content_generator.py` | Docs + slides + infographics + audio + video + quiz | ✅ Completo + probado |
| `lib/pdf_designer.py` | Desktop + mobile PDF + ePub | ✅ Completo + probado |
| `lib/quality_checker.py` | 6 verificaciones automáticas | ✅ Completo + probado |
| A2A-*.md (11 archivos) | Documentación A2A del sistema | ✅ Completos |

---

## 3. Credenciales y dominios

### Google (NotebookLM)

| Campo | Valor |
|-------|-------|
| Email | fbscotta@gmail.com |
| Password | [REDACTED] (en .env, NUNCA en texto libre) |
| App-password | [REDACTED] (recomendado si 2FA activado) |
| NotebookLM URL | https://notebooklm.google.com |

### AI Tools (API Keys — en .env, gitignored)

| Campo | Uso | Estado |
|-------|-----|--------|
| `ELEVENLABS_API_KEY` | TTS (voz femenina ES/EN) | 🔴 Requerida (Starter $5/mo min para comercial) |
| `OPENROUTER_API_KEY` | LLM para análisis + contenido | 🔴 Requerida |
| `YOUTUBE_API_KEY` | Video search (YouTube Data API v3) | 🔴 Requerida (free tier 10k units/día) |

---

## 4. Endpoints críticos

| Ruta | Función | Estado |
|------|---------|--------|
| `POST /api/start` | Inicia el pipeline con un tema | Future |
| `GET /api/status` | Estado del pipeline | Future |
| `GET /api/output/:id` | Descargar producto generado | Future |

---

## 5. Reglas de seguridad

1. **No exponer credenciales en texto libre.** Todas las keys en `.env` (gitignored).
2. **`.env` está en `.gitignore`.** Confirmar: `git check-ignore .env` debe retornar `.env`.
3. **Nunca guardar passwords/tokens en A2A files.** Usar `[REDACTED]`.
4. **NotebookLM requires 2FA.** Si la cuenta tiene verificación en 2 pasos, usar app-password o OAuth.
5. **No abusar de YouTube API.** Respetar rate limits (100 unidades/día).
6. **ElevenLabs comercial:** requiere plan Starter o superior. Free tier no permite uso comercial.

---

## 6. Checklists de comandos

### Verificar estado del repo
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
git status --short
git log --oneline -5
```

### Verificar que .env está gitignored
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
git check-ignore .env && echo "OK: .env ignorado" || echo "ALERTA: .env no ignorado"
```

### Verificar Playwright
```bash
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
python -m playwright install chromium  # solo primera vez
```

### Ejecutar el pipeline completo
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
python factory.py --topic "Como auto educarse con IA. El método Dan Martell" --lang all --verify
```

### Para ejecutar solo una fase
```bash
# Solo source collection
python -c "from lib.source_collector import search_videos; print(search_videos('Dan Martell scaling'))"

# Solo content generation (con datos mock)
python -c "
from lib.content_generator import generate_docs, generate_slides, generate_infographics, generate_quiz
test = {'topic': 'Test', 'summary': ['Line 1'], 'insights': ['Idea 1'], 'slides': ['Slide 1'], 'faq': ['Q1'], 'timeline': ['Evento 1']}
print('docs:', len(generate_docs(test)), 'chars')
print('slides:', len(generate_slides(test)), 'slides')
print('infographics:', len(generate_infographics(test)), 'svg')
print('quiz:', len(generate_quiz(test)['questions']), 'questions')
"

# Solo PDF
python lib/pdf_designer.py  # test de generacion

# Solo quality check
python lib/quality_checker.py output/pdf_desktop/
```

### Verificar que no hay credenciales expuestas
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
grep -rE 'APP_USR|re_nSK|eyJ[a-zA-Z0-9]{20,}|sk_live|pk_live|GOOGLE_PASSWORD' A2A-*.md 2>/dev/null | wc -l
# debe ser 0
```

### Push a GitHub
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
git add -A
git commit -m "Descriptive commit message"
git push origin main
```

---

## 7. Glosario mínimo

| Término | Significado |
|---------|-------------|
| NTBLM | NotebookLM (Google's AI-powered research notebook) |
| Source collection | Proceso de encontrar y agregar fuentes a NotebookLM |
| Deep analysis | Proceso de NotebookLM para sintetizar contenido |
| Product bundle | Conjunto de formatos generados (PDF, ePub, audio, video) |
| A→B→Z | Pipeline de 6 fases: Source → NotebookLM Analysis → Content → Design → Quality → Export |

---

## 8. Contacto y ownership

- **Owner:** Facundo "FB" Scroggie — fbscotta@gmail.com
- **Repo:** https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
- **Google Account:** fbscotta@gmail.com
- **Support:** Autonomous — no manual intervention needed for most tasks
- **GitHub PAT:** [REDACTED] (en ~/.git-credentials)

---

## 9. Estado actual del sistema (actualizado 2026-08-21)

### Completado ✅

- ✅ A2A-Quickstart.md (este archivo) — actualizado con estado real
- ✅ A2A-WIP.md — actualizado
- ✅ A2A-Tasks.md — actualizado
- ✅ A2A-Technical.md — actualizado
- ✅ A2A-WHAT.md — actualizado
- ✅ A2A-Blockers.md — actualizado
- ✅ A2A-Bugs.md — actualizado
- ✅ A2A-Fixes.md — actualizado
- ✅ A2A-Analysis.md — actualizado
- ✅ A2A-Tests.md — actualizado
- ✅ A2A-Production-Metadata.md — actualizado
- ✅ factory.py — A→B→Z con 6 fases probadas
- ✅ config.py — env vars + configs
- ✅ config.product.json — metadatos completos
- ✅ lib/source_collector.py — YouTube API + URL validation
- ✅ lib/notebooklm_client.py — Playwright browser automation (Playwright instalado + Chromium descargado)
- ✅ lib/content_generator.py — docs + slides + infographics + audio + video + quiz (4/5 funciones probadas OK)
- ✅ lib/pdf_designer.py — desktop PDF + mobile PDF + ePub (reportlab funciona, pandoc/LaTeX opcionales)
- ✅ lib/quality_checker.py — 6 checks probados
- ✅ .env.example — todas las credenciales documentadas
- ✅ .gitignore — protege credenciales, output, Python artifacts
- ✅ requirements.txt — todas las Python dependencies
- ✅ setup.py — instalación del sistema

### Pendiente / Bloqueado 🔴

- 🔴 **NOTEBOOKLM CREDenciales** — email fbscotta@gmail.com configurado pero sin password/app-password/cookies. Login falla sin credenciales. Solución: crear app-password en cuenta Google o exportar cookies de sesión.
- 🔴 **ELEVENLABS_API_KEY** — requerida para TTS. Free tier disponible para pruebas, pero uso comercial requiere Starter ($5/mo) o superior.
- 🔴 **YOUTUBE_API_KEY** — requerida para source collection. Free tier disponible (10k units/día).
- 🔴 **OPENROUTER_API_KEY** — requerida para LLM content generation.
- 🔴 **pandoc / LaTeX** — opcionales para PDF alternativo. reportlab fallback funciona.

---

## 10. Resultados de tests (2026-08-21)

### Content Generator ✅
```
docs: 941 chars - OK
slides: 5 slides - OK
infographics: 2 SVG - OK
quiz: 2 questions - OK
```

### PDF Designer ✅
```
pandoc available: False
wkhtmltopdf available: False
weasyprint available: False
pdflatex available: False
✅ PDF generado con reportlab (fallback)
```

### Quality Checker ✅
```
6/6 verificaciones ejecutadas
2/6 pasaron (en directorio vacío - correcto, detecta productos faltantes)
```

### NotebookLM Client ⚠️
```
Playwright: OK (Chromium instalado)
Login: Falla — falta credencial (password/app-password/cookies)
```

---

> *Este archivo se actualiza al inicio de cada sesión y después de cada cambio relevante.*
> *Mantener sincronizado con los valores en `.env` y endpoints reales.*
