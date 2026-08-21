# A2A Bugs — Registro de bugs

> Bugs encontrados en AIIA-NTBLM-Factory o en sus dependencias.
> Updated: 2026-08-21. All times UTC-3. Status: INFRAESTRUCTURA COMPLETA

---

## Bugs resueltos ✅

| ID | Issue | Fix | Date |
|----|-------|-----|------|
| BUG-FIXED-1 | A2A file structure missing | 11 A2A files creados | 2026-08-21 |
| BUG-FIXED-2 | factory.py sin código | factory.py creado con 6 fases A→B→Z | 2026-08-21 |
| BUG-FIXED-3 | lib/ sin módulos | 5 módulos creados | 2026-08-21 |
| BUG-FIXED-4 | Playwright no instalado | Playwright + Chromium instalados | 2026-08-21 |
| BUG-FIXED-5 | Content Generator sin funciones | docs, slides, infographics, quiz creados y probados | 2026-08-21 |
| BUG-FIXED-6 | PDF Designer sin funciones | reportlab funciona como PDF fallback | 2026-08-21 |
| BUG-FIXED-7 | Quality Checker sin checks | 6 checks creados y probados | 2026-08-21 |
| BUG-FIXED-8 | .env.example faltante | .env.example creado con todas las credenciales | 2026-08-21 |
| BUG-FIXED-9 | .gitignore faltante | .gitignore creado (protege .env, output/, Python artifacts, LaTeX) | 2026-08-21 |
| BUG-FIXED-10 | requirements.txt faltante | requirements.txt creado | 2026-08-21 |
| BUG-FIXED-11 | config.product.json faltante | config.product.json creado con metadatos completos | 2026-08-21 |
| BUG-FIXED-12 | Content Generator SVG NameError | generate_infographics() f-strings causando NameError (font/arrow/box no definidos) — reescrito con string concatenation | 2026-08-21 |
| BUG-FIXED-13 | Quality Checker summary() TypeError | summary() usando zip(self.checks_ran, self.checks_passed) donde checks_passed es int no list — reescrito con self._last_results | 2026-08-21 |

---

## Bugs activos (con trabajo alrededor)

| ID | Issue | Severity | Workaround | Estado |
|----|-------|----------|------------|--------|
| BUG-01 | NotebookLM UI puede cambiar, rompiendo Playwright selectors | Medium | Usar selectores basados en texto + retry con alternativas | Open — manejado con selectores adaptativos + retry |
| BUG-02 | ElevenLabs voice gender puede no coincidir con accent solicitado | Low | Verificar voice ID antes de TTS, fallback voice si no disponible | Open — manejado con verificacion de voz |
| BUG-03 | YouTube search puede devolver videos irrelevantes | Medium | Filtro por keywords + channel verification + manual curation | Open — manejado con filtrado |
| BUG-04 | LaTeX puede fallar con caracteres especiales o contenido muy largo | Medium | Sanitizar contenido antes de compilación, usar reportlab fallback | Open — manejado con sanitization + fallback |
| BUG-05 | Audio duration puede no coincidir con expected page count | Low | Estimar word count → duración esperada, ajustar TTS speed | Open — manejado con estimación |

---

## Estado de bugs

| Bug | Severity | Priority | Owner | Target Fix |
|-----|----------|----------|-------|------------|
| BUG-01 | Medium | High | AIIA | Antes de primer uso de NotebookLM |
| BUG-02 | Low | Medium | AIIA | Antes de primera generación de audio |
| BUG-03 | Medium | High | AIIA | Antes de primer source collection |
| BUG-04 | Medium | High | AIIA | Antes de primera generación de PDF |
| BUG-05 | Low | Low | AIIA | Fase posterior |

**Total bugs activos:** 5 (todos con workaround disponible)
**Total bugs resueltos:** 13

---

## Bug triage process

Cada bug:
1. Documentado aquí con ID, issue, severity, workaround, estado
2. Si se resuelve: movido a "Bugs resueltos" con fix + date
3. Si se descubre nuevo bug: agregado a "Bugs activos"

---

> Updated: 2026-08-21. Status: INFRAESTRUCTURA COMPLETA. Next review: after first production pipeline run.
