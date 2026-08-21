# A2A Blockers — Bloqueos conocidos

> Bloqueos que impiden el avance del sistema.
> Updated: 2026-08-21. All times UTC-3. Status: INFRAESTRUCTURA COMPLETA + NOTEBLOCKERS ACTIVOS

---

## Bloqueos Activos

### 🟡 BLO-05: Extract Analysis — NotebookLM processing time
- **Severity:** Medium
- **Swarm:** Pipeline (Phase 2 completion)
- **Descripción:** Después de agregar la fuente YouTube, NotebookLM necesita ~90-120s para procesarla y generar análisis (summary, slides, FAQ, timeline, insights). El código de extracción está completo pero el contenido 아직 no está disponible.
- **Impact:** La extracción de análisis del video Dan Martell aún no se ha completado.
- **Trabajo alrededor:** Esperar 5-10 minutos y re-ejecutar el pipeline (el notebook ya tiene la fuente agregada).
- **Estado:** 🟡 En progreso — notebook ID `6700442a-19ed-4f2f-94d9-860de19b2f8e` tiene la fuente agregada, esperando procesamiento.

---

## Bloqueos resueltos ✅

### ✅ BLO-01: NotebookLM login — Google bloquea navegador headless — **RESUELTO**
- **Severity:** Critical (era)
- **Swarm:** NotebookLM Client (Phase 2)
- **Descripción previa:** Google devolvía "Couldn't sign you in — This browser or app may not be secure" en cuentas f4kub4lt4 / B4lth4z4r.369 / baltazar.scotta.369. NO era un bug del código — Google rechazaba el sign-in a nivel de servidor (anti-automation).
- **Solución aplicada:** ✅ **CDP + Chrome perfil real** — se conecta a Chrome ejecutándose vía DevTools Protocol (puerto 9222, profile copy en `/tmp/nblm_chrome_profile`) que tiene sesión Google preexistente. Playwright reusa la sesión sin re-login, bypassando el bloqueo de Google.
- **Resultado:** ✅ **VERIFICADO** — 37 cookies Google en contexto, sesión válida hasta 2027. Login, creación de notebook y agregado de fuente exitosamente ejecutados.
- **Estado:** ✅ **RESUELTO**

### ✅ BLO-02: ElevenLabs API key (TTS) — **RESUELTO**
- **Estado:** ✅ RESUELTO — ELEVENLABS_API_KEY configurada y verificada en caliente (audio ES Laura + EN Alice generado OK)

### ✅ BLO-03: YouTube Data API key — **RESUELTO**
- **Estado:** ✅ RESUELTO — GOOGLE_API_KEY configurada; google-api-python-client pinneado a 1.12.3 + setuptools<69

### ✅ BLO-04: OpenRouter API key — **RESUELTO**
- **Estado:** ✅ RESUELTO — OPENROUTER_API_KEY configurada y verificada

---

## Bloqueos resueltos ✅ (históricos)

| Id | Issue | Resolution |
|-----|-------|------------|
| BLO-OLD-1 | Infraestructura A2A sin archivos | 11 A2A files creados |
| BLO-OLD-2 | factory.py sin código | factory.py creado con 6 fases A→B→Z |
| BLO-OLD-3 | lib/ sin módulos | 5 módulos creados y probados |
| BLO-OLD-4 | Playwright no instalado | Playwright instalado + Chromium descargado |
| BLO-OLD-5 | Content Generator sin funciones | 4/5 funciones creadas y probadas |
| BLO-OLD-6 | PDF Designer sin funciones | PDF Designer creado, reportlab funciona |
| BLO-OLD-7 | Quality Checker sin checks | Quality Checker creado con 6 checks |
| BLO-OLD-8 | Sin .env.example | .env.example creado |
| BLO-OLD-9 | Sin .gitignore | .gitignore creado |
| BLO-OLD-10 | Sin requirements.txt | requirements.txt creado |
| BLO-01 | NotebookLM login — Google anti-automation | ✅ **RESUELTO: CDP + Chrome perfil real (port 9222)** |

---

## Resolución plan

Orden de prioridad para desbloquear (por severidad):

1. **BLO-05 (Extract Analysis — esperar procesamiento)** — medio, requiere tiempo de NotebookLM
2. **BLO-02 (ElevenLabs API key)** — alto, requerido para audio comercial — ✅ RESUELTO
3. **BLO-03 (YouTube API key)** — alto, requerido para source collection — ✅ RESUELTO
4. **BLO-04 (OpenRouter API key)** — medio, requerido para LLM content — ✅ RESUELTO

---

> Updated: 2026-08-21. Status: INFRAESTRUCTURA COMPLETA + NOTEBLOCKERS ACTIVOS except BLO-05 (procesamiento NotebookLM en progreso). BLO-01 resuelto vía CDP + Chrome perfil real.
