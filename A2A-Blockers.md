# A2A Blockers — Bloqueos conocidos

> Bloqueos que impiden el avance del sistema.
> Updated: 2026-08-21. All times UTC-3. Status: INFRAESTRUCTURA COMPLETA

---

## Blockers Activos

### 🔴 BLO-01: Credenciales NotebookLM (login a notebooklm.google.com)
- **Severity:** Critical
- **Swarm:** NotebookLM Client (Phase 2)
- **Blocked by:** Google cuenta fbscotta@gmail.com requiere credenciales para login
- **Impact:** No se puede ejecutar el pipeline completo — Phase 2 falla sin login
- **Trabajo alrededor disponible:**
  - Opción A: app-password de Google (recomendado si 2FA activado)
  - Opción B: cookies de sesión guardadas (~/.aiia-ntblm/notebooklm_cookies.json o GOOGLE_SESSION_COOKIE env var)
  - Opción C: NOTEBOOKLM_PASSWORD (no recomendado si 2FA activado)
- **Estado:** 🔴 Blocked — credenciales no configuradas
- **Solución requerida:** FB configura NOTEBOOKLM_APP_PASSWORD o exporta cookies de sesión al .env

### 🔴 BLO-02: ElevenLabs API key (TTS)
- **Severity:** High
- **Swarm:** Content Generation (Phase 3 — audio)
- **Blocked by:** ElevenLabs requiere plan de pago para uso comercial
- **Impact:** No se puede generar audio de calidad comercial sin API key + plan paid
- **Trabajo alrededor disponible:**
  - Free tier disponible para pruebas (no comercial)
  - Para uso comercial: necesitas ElevenLabs Starter ($5/mo) o Creator plan
  - Alternativa TTS: Google Cloud TTS, Amazon Polly (pero ElevenLabs tiene mejor calidad + voces femeninas LatAm/British)
- **Estado:** 🔴 Blocked — ELEVENLABS_API_KEY no configurada
- **Solución requerida:** FB configura ELEVENLABS_API_KEY y plan de pago si se requiere comercial

### 🔴 BLO-03: YouTube Data API key
- **Severity:** High
- **Swarm:** Source Collection (Phase 1)
- **Blocked by:** YouTube Data API v3 requiere API key
- **Impact:** No se puede buscar videos de YouTube automáticamente
- **Trabajo alrededor disponible:**
  - Free tier: 10,000 units/día — suficiente para búsquedas limitadas
  - Alternativa: búsqueda manual + paste de URLs
  - Caché de resultados en output/ para evitar búsquedas repetidas
- **Estado:** 🔴 Blocked — YOUTUBE_API_KEY no configurada
- **Solución requerida:** FB configura YOUTUBE_API_KEY en Google Cloud Console

### 🔴 BLO-04: OpenRouter API key
- **Severity:** Medium
- **Swarm:** Content Generation (Phase 3 — docs, quiz)
- **Blocked by:** LLM para generación de contenido requiere API key
- **Impact:** Content generation puede usar datos mock/generics sin LLM
- **Trabajo alrededor disponible:**
  - Contenido puede generarse con datos mock para testing
  - Para producción: necesitas OpenRouter API key
- **Estado:** 🔴 Blocked — OPENROUTER_API_KEY no configurada
- **Solución requerida:** FB configura OPENROUTER_API_KEY

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
