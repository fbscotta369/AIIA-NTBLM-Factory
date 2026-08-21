# A2A WHAT — Respuestas a preguntas clave del sistema

> Documento que responde las 7 preguntas fundamentales sobre AIIA-NTBLM-Factory v1.0.
> Updated: 2026-08-21. All times UTC-3. Status: INFRAESTRUCTURA COMPLETA

---

## 1. ¿Cuál es la URL/ubicación de este website/app?

**NotebookLM (análisis):** https://notebooklm.google.com (browser automation via Playwright)

**Repo GitHub:** https://github.com/fbscotta369/AIIA-NTBLM-Factory.git

**Código local:** /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory

**Google Account (propietario):** fbscotta@gmail.com

**Plataformas de venta objetivo:** Amazon KDP, Shopify, Hotmart, Gumroad, Lemon Squeezy, Payhip.

**Estado actual:** Infraestructura completada provisionalmente. Pipeline listo para ejecutar cuando credenciales configuradas.

---

## 2. ¿Este sistema genera productos? ¿Cuáles?

Sí. Genera **libros digitales vendibles** en 2 idiomas a partir de un tema. Los productos incluyen:

| Producto | Formato | Idiomas | Descripción | Estado del módulo |
|----------|---------|---------|-------------|-------------------|
| PDF Desktop | PDF (A4) | ES (LatAm) + EN (British) | Libro digital profesional para descarga/venta | `pdf_designer.py` (reportlab funciona) |
| PDF Mobile | PDF (A5) | ES (LatAm) + EN (British) | Versión optimizada para móvil | `pdf_designer.py` |
| ePub | ePub | ES (LatAm) + EN (British) | E-reader (Kindle, Apple Books, etc.) | `pdf_designer.py` (pandoc opcional) |
| Audio | MP3 | ES (LatAm/female) + EN (British/female) | Narración completa del libro con ElevenLabs TTS | `content_generator.py` (requiere API key) |
| Video | MP4 | ES (LatAm) + EN (British) | Diapositivas animadas con narración (FFmpeg) | `content_generator.py` (requiere FFmpeg) |
| Quiz | Markdown/JSON | ES (LatAm) + EN (British) | Preguntas de comprensión | `content_generator.py` |

**Ejemplo de producto** (tema: "Como auto educarse con IA. El método Dan Martell"):

| Característica | Valor |
|---------------|-------|
| Título | Cómo auto educarse con IA: El método Dan Martell |
| Tipo | Libro digital + audio + video + quiz |
| Lenguas | Español (LatAm, voz femenina) + English (British, voz femenina) |
| Fuente primaria | Videos de YouTube buscados con YouTube Data API v3 |
| Análisis profundo | NotebookLM (resúmenes, slides, FAQ, timeline) vía Playwright |
| Análisis extraído | summary, slides, faq, timeline, insights |
| Productos generados | PDF desktop + mobile, ePub, MP3 audio, MP4 video, quiz |

---

## 3. ¿Cuál es el buyer persona / target audience?

### Buyer Persona
- **Perfil:** Profesionales hispanohablantes interesados en autoeducación con IA
- **Geografía:** Latinoamérica (Argentina, México, Colombia, Chile, Perú) + España
- **Edad:** 22-45 años
- **Situación:** Profesionales, freelancers, emprendedores
- **Necesidad:** Aprender sobre autoeducación con IA de forma estructurada
- **Barreras:** No saben por dónde empezar, hay mucho contenido disperso
- **Motivación:** Aprender de forma profunda, práctica, con vocabulario accesible, en español

### Target Audience Ampliado
- **Habla hispana:** autoeducación, IA, Productivity, Growth
- **Idioma:** Español (LatAm) + English (British)
- **Compradores:** Amazon KDP readers, Hotmart course buyers, Shopify digital product buyers

---

## 4. ¿Cuáles son las opciones de pago? Especificar Payment Gateway.

El sistema genera productos **listos para vender**, pero el checkout se procesa en las plataformas de venta:

| Plataforma | Productos vendidos | Forma de pago |
|------------|-------------------|---------------|
| Amazon KDP | PDF (ebook + paperback) | Amazon checkout |
| Hotmart | PDF + ePub + audio + video + quiz | Hotmart checkout (MercadoPago, cards) |
| Shopify | PDF + ePub + audio + video + quiz | Shopify Payments, Stripe, PayPal |
| Gumroad | PDF + ePub + audio + video + quiz | Gumroad checkout |
| Lemon Squeezy | PDF + ePub + audio + video + quiz | Lemon Squeezy (global tax handling) |
| Payhip | PDF + ePub + audio + video + quiz | Payhip checkout |

**Nota:** El sistema genera los archivos productos. La venta, checkout y entrega de acceso se maneja en las plataformas. Para integración directa con Stripe/PayPal en futuro, necesitamos backend de entrega de archivos.

---

## 5. ¿Cuál es el proceso de generación?

### Flujo completo (A→B→Z) — 6 fases

```
Tema (ej: "Como auto educarse con IA. El método Dan Martell")
    │
    ▼
[Phase 1: Source Collection — 300s timeout]
    • YouTube Data API v3 search → videos
    • Filtra por: canales oficiales, duración 5-30min, relevancia, vistas > 1000
    Output: lista de URLs + metadatos (title, url, channel, views, duration)

    │
    ▼
[Phase 2: NotebookLM Deep Analysis — 600s timeout]
    • Login a notebooklm.google.com (Playwright, app-password o cookies)
    • Crea notebook con el tema
    • Agrega URLs de videos como fuentes
    • Espera NotebookLM procesar (30s)
    • Extrae: summary, slides, faq, timeline, insights
    Output: análisis JSON ({summary, slides, faq, timeline, insights})

    │
    ▼
[Phase 3: Content Generation — 900s timeout]
    PASO A: Para cada idioma (es, en):
      • generate_docs(): Markdown con estructura completa
      • generate_slides(): Datos de diapositivas
      • generate_infographics(): SVG timeline + concept map
      • generate_audio(): ElevenLabs TTS (female voice)
      • generate_video(): FFmpeg slides + audio → MP4
      • generate_quiz(): Preguntas de comprensión

    Output: docs_md, slides SVG, infographics SVG, audio_mp3, video_mp4, quiz_json

    │
    ▼
[Phase 4: PDF Design — 300s timeout]
    PASO A: Para cada idioma:
      • generate_pdf(fmt="desktop"): A4, professional layout (reportlab/pandoc/LaTeX)
      • generate_pdf(fmt="mobile"): A5, phone-readable
      • generate_epub(): ePub via pandoc

    Output: pdf_desktop, pdf_mobile, epub

    │
    ▼
[Phase 5: Quality Control — 120s timeout]
    6 verificaciones automáticas (NINGUNA se salta):
    1. completeness (CRITICAL): PDF tiene intro + cuerpo + conclusión + apéndice
    2. coherence (HIGH): Secciones fluyen lógicamente sin contradicciones
    3. visual_quality (HIGH): Infografías SVG válidas, PDF con contenido visual
    4. audio_quality (MEDIUM): MP3 > 30s, > 5KB
    5. mobile_responsiveness (MEDIUM): PDF mobile existe, optimizado para móvil
    6. branding_consistency (LOW): Marca AIIA presente, colores consistentes (#1a1a2e)

    Output: results dict {check_name: {passed, message, severity}} + all_passed

    │
    ▼
[Phase 6: Export — 60s timeout]
    • Bundle final en output/<topic_slug>/
    • metadata.json con version, fecha, idiomas, checksums, resultados de calidad

    Output: output/<topic_slug>/
      ├── pdf_desktop/<lang>_<slug>_desktop.pdf
      ├── pdf_mobile/<lang>_<slug>_mobile.pdf
      ├── epub/<lang>_<slug>.epub
      ├── audio/<lang>_<slug>.mp3
      ├── video/<lang>_<slug>.mp4
      ├── quiz/<lang>_<slug>_quiz.md
      └── metadata.json
```

---

## 6. ¿Cómo se entrega el producto?

Los productos se exportan en `output/<topic_slug>/`. El propietario sube manualmente a las plataformas de venta:

- **Amazon KDP:** PDF desktop (ebook + paperback PDF)
- **Hotmart/Shopify/Gumroad/Lemon Squeezy:** Todos los formatos en bundle

**Actualmente la entrega es manual.** Para automatización futura: API de las plataformas (Hotmart API, Shopify API, Gumroad API).

---

## Resumen Executivo de las 7 preguntas

| # | Pregunta | Respuesta |
|---|----------|-----------|
| 1 | URL/ubicación | notebooklm.google.com + github.com/fbscotta369/AIIA-NTBLM-Factory + fbscotta@gmail.com |
| 2 | Productos | PDF (desktop+mobile), ePub, audio MP3, video MP4, quiz — ES (LatAm/female) + EN (British/female) |
| 3 | Buyer persona | Profesionales hispanohablantes 22-45 años, interesados en autoeducación con IA |
| 4 | Payment Gateway | Ninguno directo — productos se suben a Amazon KDP, Hotmart, Shopify, Gumroad, Lemon Squeezy |
| 5 | Proceso | Tema → Phase 1 (YouTube search) → Phase 2 (NotebookLM analysis via Playwright) → Phase 3 (Content: docs+slides+infographics+audio+video+quiz, bilingüe) → Phase 4 (PDF design: desktop+mobile+ePub) → Phase 5 (Quality: 6 checks, none skipped) → Phase 6 (Export) |
| 6 | Entrega | Manual: subir archivos a plataformas de venta |
| 7 | Escalabilidad | Fase 1: pipeline completo. Fase 2: API integrations para venta automática |

---

> Updated: 2026-08-21. Status: INFRAESTRUCTURA COMPLETA. Next review: after first end-to-end test run.
