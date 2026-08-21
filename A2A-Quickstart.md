# A2A AI Agent Quick Reference

> Referencia rápida para agentes de IA que operan sobre AIIA-NTBLM-Factory v1.0 (NotebookLM Edition).
> Se actualiza al inicio de cada sesión y después de cada cambio relevante.
> Proyecto: /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
> Repo: https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
> Actualizado: 2026-08-21

---

## 1. Rápido: qué es esto

**AIIA-NTBLM-Factory** es una fábrica de productos digitales impulsada por NotebookLM. Toma el contenido de un tema (videos de YouTube, artículos, fuentes), lo procesa profundamente con NotebookLM, y genera productos digitales vendibles en múltiples formatos y idiomas:

- PDF diseñado (desktop + mobile optimizado)
- ePub (e-reader)
- Audio (narración)
- Video (presentación)
- Slides / infografías / quizzes

**Stack:** Python orchestrator + Browser automation (Selenium/Playwright) + NotebookLM + AI tools (ElevenLabs, BFL, Manim, Mermaid) + LaTeX/markdown PDF engine.

**Owner:** Facundo "FB" Scroggie (fbscotta@gmail.com)
**Google Account:** fbscotta@gmail.com (para NotebookLM)

---

## 2. Arquitectura del sistema

```
Tema (ej: "Como auto educarse con IA. El método Dan Martell")
    │
    ▼
[1. Source Collection] — Busca videos/YouTube del tema, los agrega a NotebookLM
    │
    ▼
[2. NotebookLM Deep Analysis] — Crea notebook, genera resúmenes, diapositivas, FAQ, audio
    │
    ▼
[3. Content Assembly] — Genera docs, slides, infographics, audio, video, quiz
    │
    ▼
[4. Product Design] — Combina todo en PDF (desktop + mobile), ePub, audio, video
    │
    ▼
[5. Quality Control] — 6 verificaciones automáticas
    │
    ▼
[6. Export] — PDF listo para vender (Amazon, Shopify, Hotmart, etc.)
```

### Componentes principales

| Componente | Función | Estado |
|------------|---------|--------|
| `orchestrator.py` | Controla todo el pipeline end-to-end | ✅ En desarrollo |
| `notebooklm_client.py` | Browser automation para login + gestion de notebooks | 🔴 Pendiente |
| `source_collector.py` | Busca fuentes de YouTube + web sobre el tema | 🔴 Pendiente |
| `content_generator.py` | Genera docs, slides, infographics, audio, video, quiz | 🔴 Pendiente |
| `pdf_designer.py` | Combina todo en PDF (desktop + mobile) + ePub | 🔴 Pendiente |
| `quality_checker.py` | 6 verificaciones automáticas de calidad | 🔴 Pendiente |

---

## 3. Credenciales y dominios

### Google (NotebookLM)
| Campo | Valor |
|-------|-------|
| Email | fbscotta@gmail.com |
| Password | [REDACTED] (en .env) |
| NotebookLM URL | https://notebooklm.google.com |

### AI Tools (API Keys en .env)
| Campo | Uso |
|-------|-----|
| `ELEVENLABS_API_KEY` | TTS (voz femenina ES/EN) |
| `OPENROUTER_API_KEY` | LLM para análisis y generación |
| `GOOGLE_API_KEY` | Gemini para análisis profundo |
| `SUPABASE_URL` | DB para tracking de productos |
| `SUPABASE_SERVICE_ROLE_KEY` | [REDACTED] |

---

## 4. Endpoints críticos

| Ruta | Función | Estado |
|------|---------|--------|
| `POST /api/start` | Inicia el pipeline con un tema | Pendiente |
| `GET /api/status` | Estado del pipeline | Pendiente |
| `GET /api/output/:id` | Descargar producto generado | Pendiente |

---

## 5. Reglas de seguridad

1. **No exponer credenciales en texto libre.** Todas las keys en `.env` (gitignored).
2. **`.env` está en `.gitignore`.** Confirmar: `git check-ignore .env` debe retornar `.env`.
3. **Nunca guardar passwords/tokens en A2A files.** Usar `[REDACTED]`.
4. **NotebookLM requires 2FA.** Si la cuenta tiene verificación en 2 pasos, usar app-password o OAuth.
5. **No abusar de YouTube API.** Respetar rate limits (100 unidades/día).

---

## 6. Checklists de comandos

### Verificar estado del repo
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
git status --short
git log --oneline -5
```

### Verificar que .env está gitignored
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
git check-ignore .env && echo "OK: .env ignorado" || echo "ALERTA: .env no ignorado"
```

### Ejecutar el pipeline
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
python3 orchestrator.py --topic "Como auto educarse con IA. El método Dan Martell" --lang es --voice female
```

### Verificar que no hay credenciales expuestas
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
grep -rE 'APP_USR|re_nSK|eyJ[a-zA-Z0-9]{20,}|sk_live|pk_live|GOOGLE_PASSWORD' A2A-*.md 2>/dev/null | wc -l
# debe ser 0
```

### Push a GitHub
```bash
cd /home/fb/Downloads/Projects/Git/AIIA-NTBLM-Factory
git add -A
git commit -m "Descriptive commit message"
git push origin main
```

---

## 7. Glosario mínimo

| Término | Significado |
|---------|-------------|
| NTBLM | NotebookLM (Google's AI-powered research notebook) |
| Source collection | Proceso de encontrar y agregar fuentes a NotebookLM |
| Deep analysis | Proceso de NotebookLM para sintetizar contenido |
| Product bundle | Conjunto de formatos generados (PDF, ePub, audio, video) |

---

## 8. Contacto y ownership

- **Owner:** Facundo "FB" Scroggie — fbscotta@gmail.com
- **Repo:** https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
- **Google Account:** fbscotta@gmail.com
- **Support:** Autonomous — no manual intervention needed for most tasks

---

> *Este archivo se actualiza al inicio de cada sesión y después de cada cambio relevante.*
> *Mantener sincronizado con los valores en `.env` y endpoints reales.*