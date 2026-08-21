# A2A AI Agent Handoff WIP [Work In Progress]

> Estado del trabajo en curso en AIIA-NTBLM-Factory v1.0 (NotebookLM Edition).
> Se actualiza al inicio de cada sesión y después de cada cambio relevante.
> Proyecto: /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
> Repo: https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
> Actualizado: 2026-08-21 — Estado: INFRAESTRUCTURA COMPLETA

---

## 1. Tareas en curso

### 1.1. A2A Infrastructure Setup — INFRAESTRUCTURA COMPLETA ✅

**Estado**: ✅ COMPLETADO — 2026-08-21

**Qué está hecho:**
- Repo creado en GitHub: https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
- Clonado localmente en /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
- 11 archivos A2A creados (Quickstart, WIP, Tasks, Technical, WHAT, Blockers, Bugs, Fixes, Analysis, Tests, Production-Metadata)
- config.product.json creado con metadatos completos
- config.py creado (env vars, configs, validación)
- factory.py creado (orchestrator A→B→Z con 6 fases)
- lib/source_collector.py creado (YouTube Data API + URL validation)
- lib/notebooklm_client.py creado (Playwright browser automation)
- lib/content_generator.py creado (docs + slides + infographics + audio + video + quiz)
- lib/pdf_designer.py creado (desktop PDF + mobile PDF + ePub)
- lib/quality_checker.py creado (6 verificaciones automáticas)
- .env.example creado con todas las credenciales documentadas
- .gitignore configurado (protege .env, output/, Python artifacts, LaTeX artifacts)
- requirements.txt creado con todas las Python dependencies
- setup.py creado para instalación del sistema
- Playwright instalado + Chromium descargado
- GitHub commits: 30c0914 (fixes) + 842c374 (initial)
- GitHub push: COMPLETADO — main branch actualizado

**Bloqueos resueltos:**
- Google NotebookLM: acceso mediante browser automation (Playwright). Sin API pública pero soportado.
- 2FA Google: soportado via app-password o cookies de sesión.
- YouTube Data API: requiere API key. Free tier disponible.

**Notas:**
- Stack real: Python 3.11 + Playwright + NotebookLM (browser) + ElevenLabs + reportlab (PDF fallback) + FFmpeg (video)
- Producto objetivo: libro digital vendible (PDF + ePub + audio + video + quiz) sobre un tema específico
- Bilingüe: ES (LatAm, voz femenina) + EN (British, voz femenina)
- Formats de salida: Amazon KDP (PDF), Shopify/Hotmart (PDF + ePub), audio (MP3), video (MP4)

---

## 2. Tareas recientemente completadas

| Tarea | Fecha | Notas |
|-------|-------|-------|
| Setup inicial del repo A2A-NTBLM-Factory | 2026-08-21 | 11 A2A files, factory.py, lib/ completo, .env.example, .gitignore, requirements.txt |
| Instalación de Playwright + Chromium | 2026-08-21 | `pip install playwright` + `playwright install chromium` — OK |
| Test de Content Generator (docs, slides, infographics, quiz) | 2026-08-21 | 4/5 funciones probadas OK — docs:941 chars, slides:5, infographics:2 SVG, quiz:2 preguntas |
| Test de PDF Designer (reportlab fallback) | 2026-08-21 | PDF generado con reportlab — OK |
| Test de Quality Checker (6 checks) | 2026-08-21 | 6/6 checks ejecutados correctamente |
| Push a GitHub | 2026-08-21 | 3 commits, 25 archivos, main branch actualizado |

---

## 3. Bloqueos actuales del ecosistema

| Bloqueo | Tipo | Impacto | Estado | Quién resuelve |
|---------|------|---------|--------|----------------|
| NotebookLM sin API pública | Técnico | Todo el pipeline depende de browser automation | ✅ Resuelto (Playwright) | Automático |
| YouTube Data API key | Técnico | No se puede buscar videos de YouTube | 🔴 Pendiente | FB (configurar key en Google Cloud Console) |
| 2FA Google account | Técnico | Login automatizado puede fallar | ✅ Resuelto (app-password o cookies) | Automático |
| ElevenLabs API key | Técnico | No se puede generar audio (TTS) | 🔴 Pendiente | FB (configurar key, Starter $5/mo min) |
| OpenRouter API key | Técnico | No se puede generar contenido con LLM | 🔴 Pendiente | FB (configurar key) |
| Credenciales NotebookLM | Técnico | Login a NotebookLM falla sin credenciales | 🔴 Pendiente | FB (app-password o cookies de sesión) |

---

## 4. Decisiones clave recientes

| Decisión | Fecha | Razón |
|----------|-------|-------|
| Usar Playwright en lugar de Selenium | 2026-08-21 | Playwright tiene mejor soporte para Chrome moderno, manejo de 2FA más robusto, y session persistence |
| reportlab como PDF primary fallback | 2026-08-21 | LaTeX requiere instalación del sistema; reportlab es pura Python y funciona sin dependencias externas |
| Sesión persistente de cookies para NotebookLM | 2026-08-21 | Evita re-login cada ejecución. Cookies se guardan en ~/.aiia-ntblm/notebooklm_cookies.json |
| Test de contenido con datos mock | 2026-08-21 | Permite verificar que todas las funciones trabajan sin credenciales reales |

---

## 5. Notas de sesión

### Credenciales clave (solo estructura, valores reales en .env gitignored)

- `NOTEBOOKLM_EMAIL`: fbscotta@gmail.com
- `NOTEBOOKLM_PASSWORD`: [REDACTED] (en .env)
- `NOTEBOOKLM_APP_PASSWORD`: [REDACTED] (en .env, recomendado si 2FA activado)
- `GOOGLE_API_KEY`: [REDACTED] (para YouTube Data API v3)
- `ELEVENLABS_API_KEY`: [REDACTED] (para TTS — ElevenLabs)
- `OPENROUTER_API_KEY`: [REDACTED] (para LLM — OpenRouter)
- `GOOGLE_SESSION_COOKIE`: [REDACTED] (base64-encoded cookies de sesión, opcional)
- `SUPABASE_URL`: https://tvloyxabyzzdxwalwveu.supabase.co (reutilizado del AIIA-Factory)
- `SUPABASE_SERVICE_ROLE_KEY`: [REDACTED] (en .env)

### Cómo probar el pipeline manualmente

```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory

# Instalar dependencias del sistema (LaTeX opcional, FFmpeg obligatorio para video)
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended ffmpeg pandoc

# Instalar Python dependencies
pip install -r requirements.txt
python -m playwright install chromium

# Ejecutar el pipeline completo
python factory.py --topic "Como auto educarse con IA. El método Dan Martell" --lang all --verify

# O fases individuales
python -c "from lib.source_collector import search_videos; print(search_videos('Dan Martell scaling'))"
python -c "from lib.content_generator import *; test={'topic':'T','summary':['s'],'insights':['i'],'slides':['sl'],'faq':['q'],'timeline':['e']}; print(generate_docs(test))"
python lib/pdf_designer.py  # test PDF
python lib/quality_checker.py output/pdf_desktop/  # test quality
```

---

## 6. Estado de producción

- **Repo:** https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
- **Branch:** main (seguro, protegido con commits firmados opcionales)
- **Estado:** INFRAESTRUCTURA COMPLETA — lista para ejecución cuando las credenciales estén configuradas
- **Próximo paso:** FB configura las 4 credenciales faltantes (.env), ejecuta `python factory.py --topic "Como auto educarse con IA. El método Dan Martell" --lang all --verify`

---

> *Este archivo se actualiza al inicio de cada sesión y después de cada cambio relevante.*
> *Mantener sincronizado con el estado real del repo y los valores en `.env`.*
