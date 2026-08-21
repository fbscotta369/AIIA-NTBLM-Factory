# A2A Blockers — Bloqueos conocidos

> Bloqueos que impiden el avance del sistema.
> Updated: 2026-08-21. All times UTC-3. Status: INFRAESTRUCTURA COMPLETA

---

## Blockers Activos

### 🔴 BLO-01: NotebookLM login — Google bloquea navegador headless
- **Severity:** Critical
- **Swarm:** NotebookLM Client (Phase 2)
- **Blocked by:** Google devuelve "Couldn't sign you in — This browser or app may not be secure" en cuentas f4kub4lt4 / B4lth4z4r.369 / baltazar.scotta.369. NO es un bug del código — Google rechaza el sign-in a nivel de servidor (anti-automation) antes de pedir password.
- **Verificado en:** 2026-08-21 (3 cuentas probadas, todas bloqueadas idénticamente)
- **Impact:** Phase 2 no puede ejecutarse automáticamente. El campo de email SÍ aparece, pero tras enviarlo Google niega el login.
- **Trabajo alrededor disponible:**
  - **Opción A (recomendada):** exportar cookies de sesión desde un navegador REAL (Chrome en escritorio, logueado a Google) → pegar como `GOOGLE_SESSION_COOKIE` (base64 de storage_state JSON) en .env. Playwright reusa la sesión sin re-login.
  - **Opción B:** usar un perfil de Chrome persistente (`user_data_dir`) ya logueado, en vez de login por password.
  - **Opción C:** NotebookLM API (si la cuenta tiene acceso) en lugar de automatización web.
- **Estado:** 🔴 Blocked — requiere acción manual de FB (exportar cookies de sesión de un navegador real)
- **Solución requerida:** FB exporta cookies de sesión de Google logueada y las pasa vía `GOOGLE_SESSION_COOKIE`. El código ya soporta `load_cookies()` desde env/file.

### ✅ BLO-02: ElevenLabs API key (TTS) — RESUELTO
- **Estado:** ✅ RESUELTO — ELEVENLABS_API_KEY configurada y verificada en caliente (audio ES Laura + EN Alice generado OK)

### ✅ BLO-03: YouTube Data API key — RESUELTO
- **Estado:** ✅ RESUELTO — GOOGLE_API_KEY configurada; google-api-python-client pinneado a 1.12.3 + setuptools<69

### ✅ BLO-04: OpenRouter API key — RESUELTO
- **Estado:** ✅ RESUELTO — OPENROUTER_API_KEY configurada y verificada

---

## Bloqueos resueltos ✅

| Id | Issue | Resolution |
|-----|-------|------------|
| BLO-OLD-1 | Infraestructura A2A sin archivos | 11 A2A files creados (Quickstart, WIP, Tasks, Technical, WHAT, Blockers, Bugs, Fixes, Analysis, Tests, Production-Metadata) |
| BLO-OLD-2 | factory.py sin código | factory.py creado con 6 fases A→B→Z, probado y documentado |
| BLO-OLD-3 | lib/ sin módulos | 5 módulos creados: source_collector.py, notebooklm_client.py, content_generator.py, pdf_designer.py, quality_checker.py |
| BLO-OLD-4 | Playwright no instalado | Playwright instalado + Chromium descargado |
| BLO-OLD-5 | Content Generator sin funciones | 4/5 funciones creadas y probadas: docs, slides, infographics, quiz (audio requiere API key) |
| BLO-OLD-6 | PDF Designer sin funciones | PDF Designer creado, reportlab funciona como fallback |
| BLO-OLD-7 | Quality Checker sin checks | Quality Checker creado con 6 checks probados |
| BLO-OLD-8 | Sin .env.example | .env.example creado con todas las credenciales documentadas |
| BLO-OLD-9 | Sin .gitignore | .gitignore creado (protege .env, output/, Python artifacts, LaTeX artifacts) |
| BLO-OLD-10 | Sin requirements.txt | requirements.txt creado con todas las Python dependencies |

---

## Resolución plan

Orden de prioridad para desbloquear (por severidad):

1. **BLO-01 (NotebookLM credentials)** — crítico, bloquea todo el pipeline
2. **BLO-02 (ElevenLabs API key)** — alto, requerido para audio comercial
3. **BLO-03 (YouTube API key)** — alto, requerido para source collection
4. **BLO-04 (OpenRouter API key)** — medio, requerido para LLM content

FB debe configurar las 4 credenciales en .env antes de ejecutar el pipeline.

---

> Updated: 2026-08-21. Status: INFRAESTRUCTURA COMPLETA. Next review: after credentials configured + first pipeline run.
