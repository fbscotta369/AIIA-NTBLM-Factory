# A2A Tasks — Backlog + Roadmap

> Tareas pendientes, bugs conocidos, roadmap y mantenimiento para AIIA-NTBLM-Factory.
> Estado actualizado: 2026-08-21

---

## 1. Tareas activas

### T1: Setup del repositorio y estructura A2A ✅ COMPLETADA

**Prioridad:** Crítica
**Estado:** ✅ COMpletada
**Bloqueos:** Ninguno
**Cómo actualizar cuando se complete:** Ya completada — marcar como histórico.

**Detalles:**
- Repo creado en GitHub ✅
- Clonado localmente ✅
- A2A-Quickstart.md creado ✅
- A2A-WIP.md creado ✅
- .gitignore configurado ✅

---

### T2: Configurar environment Python y dependencias 🔴 PENDIENTE

**Prioridad:** Crítica
**Estado:** 🔴 PENDIENTE
**Bloqueos:** Ninguno (automático)
**Cómo actualizar cuando se complete:** Marcar como ✅ y mover a "Tareas recientemente completadas" en A2A-WIP.md.

**Sub-tareas:**
- [ ] Crear `requirements.txt` con todas las dependencias (playwright, elevenlabs, openrouter, etc.)
- [ ] Crear `setup.sh` para instalar dependencias e inicializar Playwright
- [ ] Verificar que Python 3.11 está disponible
- [ ] Crear `venv` o usar `uv` (project uses PEP 668)
- [ ] Configurar `.env.example` con todos los campos necesarios

---

### T3: NotebookLM browser automation client 🔴 PENDIENTE

**Prioridad:** Crítica
**Estado:** 🔴 PENDIENTE
**Bloqueos:** 2FA en cuenta Google, NotebookLM sin API pública
**Cómo actualizar:** Verificar login exitoso, crear notebook, agregar fuentes.

**Sub-tareas:**
- [ ] Instalar Playwright + browsers (`playwright install chromium`)
- [ ] Implementar `notebooklm_client.py`:
  - `login(email, password/app_password)` → navega a accounts.google.com
  - `create_notebook(title)` → crea notebook en notebooklm.google.com
  - `add_sources(urls)` → agrega URLs de YouTube/videos como fuentes
  - `get_summary()` → extrae el resumen generado por NotebookLM
  - `get_slides()` → extrae las diapositivas
  - `get_faq()` → extrae la sección de preguntas frecuentes
  - `get_audio()` → descarga el audio generado (si está disponible)
- [ ] Manejar 2FA: si la cuenta tiene verificación en 2 pasos, usar app-password o OAuth flow
- [ ] Tests: verificar que el cliente puede hacer login y navegar

---

### T4: Source collector (YouTube + web search) 🔴 PENDIETE

**Prioridad:** Alta
**Estado:** 🔴 PENDIENTE
**Bloqueos:** YouTube Data API key

**Sub-tareas:**
- [ ] Implementar `source_collector.py`:
  - `search_youtube(topic, max_results=10)` → busca videos relacionados al tema
  - `extract_video_urls(search_results)` → extrae URLs de videos de YouTube
  - Filtrar por relevancia, duración mínima (ej: >5 min), canales oficiales
  - `search_web(topic)` → búsqueda web adicional (DuckDuckGo/SearXNG)
- [ ] Configurar YouTube Data API v3 key en Google Cloud Console
- [ ] Para el ejemplo "Dan Martell": buscar videos oficiales del canal de Dan Martell + temas relacionados (auto-educación, IA, scaling)

---

### T5: Content generator (docs, slides, infographics, audio, video, quiz) 🔴 PENDIENTE

**Prioridad:** Alta
**Estado:** 🔴 PENDIENTE
**Bloqueos:** Depende de T3 (NotebookLM client) y T4 (source collection)

**Sub-tareas:**
- [ ] Extraer contenido de NotebookLM (resúmenes, slides, FAQ, timeline, etc.)
- [ ] Generar documentación (markdown → LaTeX):
  - `generate_spanish_doc()` → contenido en español (LatAm) femenino
  - `generate_english_doc()` → contenido en inglés (British) femenino
- [ ] Generar infografías (usar Mermaid/Beautiful Mermaid):
  - Diagramas de flujo, timelines, concept maps
- [ ] Generar audio (ElevenLabs):
  - Narración del libro en ES (LatAm, female)
  - Narración del libro en EN (British, female)
- [ ] Generar video:
  - Presentación de diapositivas con narración + música de fondo
  - Usar Manim para animaciones educativas o p5.js para visualizaciones
- [ ] Generar quiz:
  - Preguntas de comprensión basadas en el contenido
  - Formato: múltiple choice, short answer, reflection questions

---

### T6: PDF designer (desktop + mobile, ePub) 🔴 PENDIENTE

**Prioridad:** Alta
**Estado:** 🔴 PENDIENTE
**Bloqueos:** Depende de T5 (content generator)

**Sub-tareas:**
- [ ] Implementar `pdf_designer.py`:
  - Combinar docs, slides, infographics en un PDF cohesionado
  - PDF desktop: tamaño carta (8.5x11"), resolución alta, para descarga
  - PDF mobile: tamaño A5 o similar, optimizado para lectura en teléfono
  - ePub: estructura navegable con capítulos, tabla de contenido
- [ ] Diseño visual:
  - Portada profesional con título, subtítulo, autor
  - Layout de magazine: encabezados, tipografía, márgenes
  - Número de página, tabla de contenido, índice
  - Infografías integradas en el flujo del documento
- [ ] Herramientas: LaTeX (para PDF profesional) + pandoc (para ePub)

---

### T7: Quality checker (6 verificaciones automáticas) 🔴 PENDIENTE

**Prioridad:** Alta
**Estado:** 🔴 PENDIENTE

**Sub-tareas:**
- [ ] Implementar `quality_checker.py` con 6 verificaciones:
  1. **Completeness:** PDF tiene todas las secciones esperadas (intro, contenido, conclusión, appendix)
  2. **Coherence:** El narrative flow entre secciones es coherente (usar LLM para verificar)
  3. **Visual quality:** Infografías están legiblemente renderizadas (verificar resolución, no cortadas)
  4. **Audio quality:** Narración de audio dura el tiempo esperado y suena claro
  5. **Mobile responsiveness:** PDF mobile se ve bien en dispositivos pequeños (verificar layout)
  6. **Branding consistency:** El estilo visual (colores, fuentes, logo) es consistente en todo el producto

---

### T8: Orchestrator (factory.py equivalent) 🔴 PENDIENTE

**Prioridad:** Crítica
**Estado:** 🔴 PENDIENTE
**Bloqueos:** Depende de T3-T7

**Sub-tareas:**
- [ ] Implementar `orchestrator.py`:
  - CLI interface: `--topic`, `--lang`, `--voice`, `--verify`
  - Coordina todo el pipeline end-to-end
  - Maneja errores y reintentos
  - Guarda logs de cada fase
  - Output: archivos en `output/<topic>/`
- [ ] Fases del pipeline:
  1. `phase1_source_collection` — buscar fuentes de YouTube/web
  2. `phase2_notebooklm_analysis` — crear notebook, agregar fuentes, extraer análisis
  3. `phase3_content_generation` — generar docs, slides, infographics, audio, video, quiz
  4. `phase4_pdf_design` — crear PDF desktop + mobile, ePub
  5. `phase5_quality_control` — 6 verificaciones automáticas
  6. `phase6_export` — bundle final listo para vender

---

### T9: Tests y validación A→B→Z 🔴 PENDIENTE

**Prioridad:** Media
**Estado:** 🔴 PENDIENTE

**Sub-tareas:**
- [ ] `tests/test_pipeline.py` — tests unitarios de cada componente
- [ ] `tests/test_e2e.py` — test end-to-end con un tema de ejemplo
- [ ] `A2A-Tests.md` — plan de prueba documentado

---

### T10: Configuración de credenciales (.env, .env.example) 🔴 PENDIENTE

**Prioridad:** Crítica
**Estado:** 🔴 PENDIENTE

**Sub-tareas:**
- [ ] Crear `.env` con credenciales reales (gitignored)
- [ ] Crear `.env.example` con placeholders
- [ ] Documentar cada variable en A2A-Quickstart.md
- [ ] Verificar que .env está en .gitignore

---

## 2. Bugs conocidos

| Bug | Severidad | Estado | Notas |
|-----|-----------|--------|-------|
| (Ninguno aún) | — | — | — |

---

## 3. Roadmap

### Fase 1: Foundation (semana 1)
- T2: Environment setup
- T3: NotebookLM client (login + basic navigation)
- T10: Configuración de credenciales

### Fase 2: Core Pipeline (semana 2-3)
- T4: Source collector (YouTube + web)
- T5: Content generator
- T6: PDF designer
- T7: Quality checker

### Fase 3: Orchestration (semana 4)
- T8: Orchestrator (end-to-end)
- T9: Tests y validación

### Fase 4: Production (semana 5)
- Calidad y optimización
- Documentación
- Prueba con el tema "Como auto educarse con IA. El método Dan Martell"
- Generar producto final completo (PDF ES + PDF EN + ePub + audio + video)

---

## 4. Cómo actualizar este archivo

1. Cuando una tarea se complete: cambiar estado a ✅ COMPLETADA, mover a "Tareas recientemente completadas" en A2A-WIP.md
2. Cuando se descubra un bug: agregar a la sección 2
3. Cuando se agregue una nueva tarea: agregar a la sección 1 con prioridad y bloqueos
4. Al finalizar una fase del roadmap: actualizar el estado en la sección 3

---

## 5. Mantenimiento recurrente

- Verificar que el browser automation sigue funcionando con los cambios de NotebookLM
- Monitorear rate limits de YouTube API y ElevenLabs
- Actualizar dependencias de Python periódicamente

---

> *Este archivo se actualiza cuando una tarea se completa, se descubre un bug, o se agrega una nueva tarea.*