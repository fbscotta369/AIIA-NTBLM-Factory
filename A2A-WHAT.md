# A2A WHAT — Respuestas a preguntas clave del sistema

> Documento que responde las 7 preguntas fundamentales sobre AIIA-NTBLM-Factory.
> Updated: 2026-08-21. All times UTC-3.

---

## 1. ¿Cuál es la URL/ubicación de este website/app?

**NotebookLM**: `https://notebooklm.google.com` (para análisis profundo de fuentes)

**Repo GitHub**: `https://github.com/fbscotta369/AIIA-NTBLM-Factory.git`

**Google Account (propietario)**: `fbscotta@gmail.com`

**Redes objetivo**: Amazon KDP, Shopify, Hotmart, Gumroad, Lemon Squeezy, Payhip.

---

## 2. ¿Este sistema genera productos? ¿Cuáles?

Sí. Genera **libros digitales vendibles** en 2 idiomas a partir de un tema. Los productos incluyen:

| Producto | Formato | Idiomas | Descripción |
|----------|---------|---------|-------------|
| PDF Desktop | PDF | ES (LatAm) + EN (British) | Libro digital profesional para descarga/venta |
| PDF Mobile | PDF | ES (LatAm) + EN (British) | Versión optimizada para móvil |
| ePub | ePub | ES (LatAm) + EN (British) | E-reader (Kindle, Apple Books, etc.) |
| Audio | MP3 | ES (LatAm/female) + EN (British/female) | Narración completa del libro |
| Video | MP4 | ES (LatAm) + EN (British) | Diapositivas animadas con narración |
| Quiz | Markdown/JSON | ES (LatAm) + EN (British) | Preguntas de comprensión |

**Ejemplo de producto** (tema: "Como auto educarse con IA. El método Dan Martell"):

| Característica | Valor |
|---------------|-------|
| Título | Cómo auto educarse con IA: El método Dan Martell |
| Tipo | Libro digital + audio + video + quiz |
| Lenguas | Español (LatAm, voz femenina) + English (British, voice female) |
| Fuente primaria | Videos oficiales del canal de Dan Martell + videos relacionados |
| Análisis profundo | NotebookLM (resúmenes, slides, FAQ, timeline) |

---

## 3. ¿Cuál es el buyer persona / target audience?

### Buyer Persona
- **Perfil**: Profesionales hispanohablantes interesados en autoeducación con IA
- **Geografía**: Latinoamérica (Argentina, México, Colombia, Chile, Perú) + España
- **Edad**: 22-45 años
- **Situación**: Profesionales, freelancers, emprendedores
- **Necesidad**: Aprender sobre autoeducación con IA de forma estructurada
- **Barreras**: No saben por dónde empezar, hay mucho contenido disperso
- **Motivación**: Aprender de forma profunda, práctica, con vocabulario accesible

### Target Audience Ampliado
- **Habla hispana**: autoeducación, IA, Productivity, Growth
- **Idioma**: Español (LatAm) + English (British)
- **Compradores**: Amazon KDP readers, Hotmart course buyers, Shopify digital product buyers

---

## 4. ¿Cuáles son las opciones de pago? Especificar Payment Gateway.

El sistema genera productos **listos para vender**, pero el checkout se procesa en las plataformas de venta:

| Plataforma | Productos vendidos | Forma de pago |
|------------|-------------------|---------------|
| Amazon KDP | PDF (ebook + paperback) | Amazon checkout |
| Hotmart | PDF + ePub + audio + video | Hotmart checkout (MercadoPago, cards) |
| Shopify | PDF + ePub + audio + video | Shopify Payments, Stripe, PayPal |
| Gumroad | PDF + ePub + audio + video | Gumroad checkout |
| Lemon Squeezy | PDF + ePub + audio + video | Lemon Squeezy (global tax handling) |
| Payhip | PDF + ePub + audio + video | Payhip checkout |

**Nota**: El sistema genera los archivos productos. La venta, checkout y entrega de acceso se maneja en las plataformas. Para integración directa con Stripe/PayPal en futuro, necesitamos backend de entrega de archivos.

---

## 5. ¿Cuál es el proceso de generación?

### Flujo completo (A→B→Z):

```
Tema (ej: "Como auto educarse con IA. El método Dan Martell")
    │
    ▼
[1. Source Collection]
    • Busca videos de YouTube sobre Dan Martell + autoeducación + IA
    • Filtra por: canales oficiales, duración > 5min, relevancia, vistas > 1k
    Output: lista de URLs + metadatos

    │
    ▼
[2. NotebookLM Deep Analysis]
    • Login a notebooklm.google.com (browser automation con Playwright)
    • Crea notebook con el tema
    • Agrega URLs de videos como fuentes
    • NotebookLM genera:
      - Resumen profundo
      - Diapositivas (slides)
      - FAQ
      - Timeline
      - Insights
    Output: análisis JSON ({summary, slides, faq, timeline, insights})

    │
    ▼
[3. Content Generation (bilingüe)]
    • ES (LatAm, female): docs, infographics, audio, video, quiz
    • EN (British, female): same via LLM + ElevenLabs EN female
    Output: archivos markdown, imágenes, audio MP3, video MP4, quiz

    │
    ▼
[4. PDF Design]
    • Combina docs + slides + infographics en PDF professional
    • Desktop: LaTeX, A4, high quality, cover page
    • Mobile: condensed, phone-readable layout
    • ePub: generated via pandoc

    Output: PDF desktop, PDF mobile, ePub

    │
    ▼
[5. Quality Control (6 verificaciones)]
    1. Completeness (todas las secciones presentes)
    2. Coherence (narrative flow coherente)
    3. Visual quality (infografías legibles)
    4. Audio quality (duración + claridad)
    5. Mobile-friendly (PDF legible en móvil)
    6. Branding consistency (colores, fuentes, estilo uniforme)

    Output: reporte de calidad + aprobación/rechazo

    │
    ▼
[6. Export]
    • Bundle final en output/<topic_slug>/
    • Listo para subir a plataformas de venta
    • metadata.json con version, fecha, idiomas, checksums

    Output: output/<topic_slug>/
      ├── pdf_desktop/
      │   ├── ES_<slug>_desktop.pdf
      │   └── EN_<slug>_desktop.pdf
      ├── pdf_mobile/
      │   ├── ES_<slug>_mobile.pdf
      │   └── EN_<slug>_mobile.pdf
      ├── epub/
      │   ├── ES_<slug>.epub
      │   └── EN_<slug>.epub
      ├── audio/
      │   ├── ES_<slug>.mp3
      │   └── EN_<slug>.mp3
      ├── video/
      │   ├── ES_<slug>.mp4
      │   └── EN_<slug>.mp4
      ├── quiz/
      │   ├── ES_<slug>_quiz.md
      │   └── EN_<slug>_quiz.md
      └── metadata.json
```

---

## 6. ¿Cómo se entrega el producto?

Los productos se exportan en `output/<topic_slug>/`. El propietario sube manualmente a las plataformas de venta:

- **Amazon KDP**: PDF desktop (ebook + paperback PDF)
- **Hotmart/Shopify/Gumroad/Lemon Squeezy**: Todos los formatos en bundle

**Actualmente la entrega es manual**. Para automatización futura: API de las plataformas (Hotmart API, Shopify API, Gumroad API).

---

## Resumen Executivo de las 7 preguntas

| # | Pregunta | Respuesta |
|---|----------|-----------|
| 1 | URL/ubicación | notebooklm.google.com + github.com/fbscotta369/AIIA-NTBLM-Factory + fbscotta@gmail.com |
| 2 | Productos | PDF (desktop+mobile), ePub, audio MP3, video MP4, quiz — ES (LatAm/female) + EN (British/female) |
| 3 | Buyer persona | Profesionales hispanohablantes 22-45 años, interesados en autoeducación con IA |
| 4 | Payment Gateway | Ninguno directo — productos se suben a Amazon KDP, Hotmart, Shopify, Gumroad, Lemon Squeezy |
| 5 | Proceso | Tema → Source collection (YouTube) → NotebookLM deep analysis → Content generation (docs, slides, infographics, audio, video, quiz) → PDF design (desktop+mobile+ePub) → Quality control (6 checks) → Export |
| 6 | Entrega | Manual: subir archivos a plataformas de venta |
| 7 | Escalabilidad | Fase 1: pipeline completo. Fase 2: API integrations para venta automática |

---

> Updated: 2026-08-21. Next review: after first end-to-end test run.
