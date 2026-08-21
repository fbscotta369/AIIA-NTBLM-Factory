# A2A AI Agent Handoff WIP [Work In Progress]

> Estado del trabajo en curso en AIIA-NTBLM-Factory v1.0 (NotebookLM Edition).
> Se actualiza al inicio de cada sesión y después de cada cambio relevante.
> Proyecto: /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
> Repo: https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
> Actualizado: 2026-08-21

---

## 1. Tareas en curso

### 1.1. Setup inicial del repositorio A2A-NTBLM-Factory

**Estado**: ✅ COMPLETADO

**Qué está hecho:**
- Repo creado en GitHub: https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
- Clonado localmente en /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
- A2A-Quickstart.md creado con arquitectura completa del sistema
- A2A-WIP.md creado (este archivo)
- .gitignore configurado (excluye .env, __pycache__, output/)

**Qué falta:**
- Crear A2A-Tasks.md (backlog)
- Crear A2A-Technical.md (especificación técnica)
- Crear A2A-WHAT.md (preguntas clave)
- Crear A2A-Analysis.md (análisis A→B→Z)
- Crear A2A-Blockers.md (bloqueos)
- Crear A2A-Bugs.md (bugs conocidos)
- Crear A2A-Fixes.md (fixes aplicados)
- Crear A2A-Production-Metadata.md (metadatos)
- Crear el código Python (orchestrator.py, notebooklm_client.py, etc.)

**Bloqueos:**
- Google NotebookLM: el acceso programático directo no está disponible. Requiere browser automation (Selenium/Playwright). Si la cuenta tiene 2FA, puede necesitar app-password.
- YouTube Data API: requiere API key configurada en Google Cloud Console.

**Notas para el agente:**
- El patrón de archivos sigue el AIIA-Factory v3.4 como referencia, adaptado para NotebookLM + contenido multilingüe (ES/EN).
- El producto objetivo es un "libro digital vendible" (PDF + ePub + audio + video) sobre un tema específico.
- Los formats de salida deben estar optimizados para: Amazon KDP (PDF), Shopify/Hotmart (PDF + ePub), plataformas de audio (MP3), plataformas de video (MP4).

### 1.2. NotebookLM browser automation client

**Estado**: 🔴 PENDIENTE — Requiere configuración de browser automation

**Qué está hecho:**
- Nada aún.

**Qué falta:**
- Instalar Playwright/Selenium en el entorno
- Implementar login a Google con `fbscotta@gmail.com`
- Navegar a https://notebooklm.google.com
- Crear un notebook nuevo
- Agregar fuentes (YouTube videos, URLs, etc.)
- Extraer resúmenes, diapositivas, FAQ, audio

**Bloqueos:**
- 2FA en la cuenta de Google: si está activada, necesita app-password o token OAuth
- NotebookLM no tiene API pública todavía (solo interface web)

**Notas para el agente:**
- Usar Playwright con Chromium headless para mayor compatibilidad
- Configurar `--remote-debugging-port` para reusar sesiones
- Siempre verificar que el login fue exitoso antes de navegar a NotebookLM

### 1.3. Pipeline de generación de contenido

**Estado**: 🔴 PENDIENTE

**Qué falta:**
- `notebooklm_client.py`: Login, crear notebook, agregar fuentes, extraer análisis
- `source_collector.py`: Buscar videos de YouTube sobre el tema
- `content_generator.py`: Generar docs, slides, infographics, audio, video, quiz
- `pdf_designer.py`: Combinar todo en PDF desktop + mobile, ePub
- `quality_checker.py`: 6 verificaciones automáticas

---

## 2. Tareas recientemente completadas

| Tarea | Fecha | Notas |
|-------|-------|-------|
| (Ninguna aún — proyecto recién creado) | — | — |

---

## 3. Bloqueos actuales del ecosistema

| Bloqueo | Tipo | Impacto | Quién resuelve |
|---------|------|---------|----------------|
| NotebookLM sin API pública | Técnico | Todo el pipeline depende de browser automation | Automático (Playwright) |
| YouTube Data API key | Técnico | No se puede buscar videos de YouTube | Automático (configurar key) |
| 2FA Google account | Técnico | Login automatizado puede fallar | Automático (app-password) |
| ElevenLabs API key | Técnico | No se puede generar audio (TTS) | Automático (configurar key) |

---

## 4. Decisiones clave recientes

| Decisión | Fecha | Razón |
|----------|-------|-------|
| (Ninguna aún) | — | — |

---

## 5. Notas de sesión

### Credenciales clave (solo estructura, valores en .env)

- `NOTEBOOKLM_EMAIL`: fbscotta@gmail.com
- `NOTEBOOKLM_PASSWORD`: [REDACTED]
- `GOOGLE_API_KEY`: [REDACTED] (para YouTube Data API y/o Gemini)
- `ELEVENLABS_API_KEY`: [REDACTED] (para TTS)
- `OPENROUTER_API_KEY`: [REDACTED] (para LLM)
- `SUPABASE_URL`: https://tvloyxabyzzdxwalwveu.supabase.co (reutilizado del AIIA-Factory)
- `SUPABASE_SERVICE_ROLE_KEY`: [REDACTED]

### Cómo probar el pipeline manualmente

```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory

# Instalar dependencias
pip install playwright  # o selenium
pip install elevenlabs openrouter google-api-python-client supabase

# Ejecutar el pipeline completo
python3 orchestrator.py --topic "Como auto educarse con IA. El método Dan Martell" --lang es --voice female --verify
```

---

> *Este archivo se actualiza al inicio de cada sesión y después de cada cambio relevante.*
> *Mantener sincronizado con el estado real del repo y los valores en `.env`.*
> *Si una tarea se completa: mover a 'Tareas recientemente completadas' y actualizar A2A-Tasks.md.*