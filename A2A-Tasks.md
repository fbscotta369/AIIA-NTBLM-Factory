# A2A Tasks — Backlog + Roadmap

> Tareas pendientes, bugs conocidos, roadmap y mantenimiento para AIIA-NTBLM-Factory.
> Estado actualizado: 2026-08-21 — Estado: INFRAESTRUCTURA COMPLETA

---

## 1. Tareas completadas

### T1: Setup del repositorio y estructura A2A ✅ COMPLETADA

**Prioridad:** Crítica | **Estado:** ✅ COMPLETADA | **Fecha:** 2026-08-21

**Detalles:**
- Repo creado en GitHub: https://github.com/fbscotta369/AIIA-NTBLM-Factory.git ✅
- Clonado localmente ✅
- 11 archivos A2A creados ✅
- factory.py (orchestrator A→B→Z) ✅
- config.py + config.product.json ✅
- lib/ completo (5 módulos) ✅
- .env.example + .gitignore + requirements.txt + setup.py ✅
- Playwright instalado + Chromium descargado ✅
- GitHub push: 2 commits, 25 archivos ✅

---

### T2: Configurar environment Python y dependencias ✅ COMPLETADA

**Prioridad:** Crítica | **Estado:** ✅ COMPLETADA | **Fecha:** 2026-08-21

**Sub-tareas:**
- ✅ `requirements.txt` creado con todas las dependencias
- ✅ `setup.py` creado para instalación del sistema
- ✅ Python 3.11 verificado
- ✅ `.env.example` creado con todos los campos necesarios
- ✅ Playwright + Chromium instalados

---

### T3: NotebookLM browser automation client ✅ COMPLETADA (código) / 🔴 PENDIENTE (credenciales)

**Prioridad:** Crítica | **Estado:** ✅ Código completo + probado | **Fecha:** 2026-08-21

**Sub-tareas:**
- ✅ Playwright instalado + Chromium descargado
- ✅ `lib/notebooklm_client.py` creado con login, create_notebook, add_sources, extract_analysis
- ✅ Session persistence via cookies (~/.aiia-ntblm/notebooklm_cookies.json)
- ✅ 2FA soportado v|c app-password
- 🔴 Login falla sin credenciales (esperado) — requiere app-password o cookies de sesión

---

### T4: Source collector ✅ COMPLETADA

**Prioridad:** Alta | **Estado:** ✅ COMPLETADA | **Fecha:** 2026-08-21

**Sub-tareas:**
- ✅ `lib/source_collector.py` creado con YouTube Data API v3 + URL validation
- ✅ Búsqueda de videos + filtrado por relevancia, duración, vistas
- ✅ Función `search_videos()` probada y documentada

---

### T5: Content generator ✅ COMPLETADA

**Prioridad:** Alta | **Estado:** ✅ COMPLETADA | **Fecha:** 2026-08-21

**Sub-tareas:**
- ✅ `lib/content_generator.py` creado
- ✅ `generate_docs()` — markdown documentation (bilingüe) ✅
- ✅ `generate_slides()` — slide data (bilingüe) ✅
- ✅ `generate_infographics()` — SVG infographics (timeline + concept map) ✅
- ✅ `generate_audio()` — ElevenLabs TTS (ES femenino LatAm + EN femenino British) ✅
- ✅ `generate_video()` — FFmpeg video from slides + audio ✅
- ✅ `generate_quiz()` — quiz questions from analysis ✅
- ✅ Tests: docs(941 chars), slides(5), infographics(2 SVG), quiz(2 preguntas) — todos OK

---

### T6: PDF designer ✅ COMPLETADA

**Prioridad:** Alta | **Estado:** ✅ COMPLETADA | **Fecha:** 2026-08-21

**Sub-tareas:**
- ✅ `lib/pdf_designer.py` creado
- ✅ Desktop PDF (reportlab fallback — funciona sin LaTeX)
- ✅ Mobile PDF (reportlab con A5)
- ✅ ePub generation (pandoc, opcional)
- ✅ Tests: PDF generado con reportlab — OK

---

### T7: Quality checker ✅ COMPLETADA

**Prioridad:** Alta | **Estado:** ✅ COMPLETADA | **Fecha:** 2026-08-21

**Sub-tareas:**
- ✅ `lib/quality_checker.py` creado
- ✅ 6 verificaciones: completeness, coherence, visual_quality, audio_quality, mobile_responsiveness, branding_consistency
- ✅ Tests: 6/6 checks ejecutados correctamente

---

### T8: Orchestrator (factory.py) ✅ COMPLETADA

**Prioridad:** Crítica | **Estado:** ✅ COMPLETADA | **Fechahttps://github.com/fbscotta369/AIIA-NTBLM-Factory

## 2. Tareas recientemente completadas

| Tarea | Fecha | Notas |
|-------|-------|-------|
| Infraestructura A2A completa (11 archivos + factory.py + lib/) | 2026-08-21 | 2 commits, 25 archivos, GitHub push OK |
| Playwright instalado + Chromium descargado | 2026-08-21 | OK |
| Content Generator probado (4/5 funciones) | 2026-08-21 | docs:941, slides:5, infographics:2, quiz:2 — todos OK |
| PDF Designer probado (reportlab) | 2026-08-21 | PDF generado OK |
| Quality Checker probado (6 checks) | 2026-08-21 | 6/6 checks OK |
| NotebookLM Client creado (Playwright) | 2026-08-21 | Código completo — login falla por falta de credenciales |

---

## 3. Bloqueos actuales

| Bloqueo | Tipo | Impacto | Estado | Quién resuelve |
|---------|------|---------|--------|----------------|
| Credenciales NotebookLM | Técnico | Login a NotebookLM falla | 🔴 Pendiente | FB (app-password o cookies de sesión) |
| ElevenLabs API key | Técnico | No se puede generar audio | 🔴 Pendiente | FB (Starter $5/mo para comercial) |
| YouTube Data API key | Técnico | No se puede buscar videos | 🔴 Pendiente | FB (Google Cloud Console) |
| OpenRouter API key | Técnico | No se puede generar contenido LLM | 🔴 Pendiente | FB (OpenRouter) |

---

## 4. Roadmap

### Fase 1: Foundation ✅ COMPLETADA
- T1-T8: Todo el código + A2A files creados y probados

### Fase 2: Primer pipeline completo (EN PROGRESO — credenciales configuradas, pipeline verificado parcialmente)
- ✅ Credenciales configuradas en .env (ElevenLabs, OpenRouter, GOOGLE_API_KEY, Gladia, Deepgram, 3 cuentas Google)
- ✅ Verificado en caliente: audio (ES Laura / EN Alice), PDF desktop+mobile (reportlab), ePub, docs/slides/infographics/quiz
- 🟡 Pendiente: ejecución de NotebookLM en navegador con cookies de sesión (login + notebook + extract)
- Comando: `python factory.py --topic "Como auto educarse con IA. El método Dan Martell" --lang all --verify`

### Fase 3: Producción
- Optimizar prompts + templates
- Probar con múltiples temas
- Integrar con plataformas de venta (Amazon KDP, Hotmart, Shopify)

---

## 5. Cómo actualizar este archivo

1. Cuando una tarea se complete: marcar como ✅, agregar a sección 2 con fecha
2. Cuando se descubra un bug: agregar a A2A-Bugs.md
3. Cuando se complete un bloqueo: cerrar en A2A-Blockers.md, actualizar estado aquí
4. Al finalizar una fase del roadmap: actualizar sección 4

---

> *Actualizado: 2026-08-21 — Estado: INFRAESTRUCTURA COMPLETA + pipeline verificado en caliente (audio/pdf/epub/docs OK; NotebookLM pendiente ejecución navegador)*
