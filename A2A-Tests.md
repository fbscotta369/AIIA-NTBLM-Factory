# A2A Tests — Plan de verificación

> Plan de prueba para AIIA-NTBLM-Factory v1.0.
> Updated: 2026-08-21. All times UTC-3.

---

## Objetivo

Verificar que el pipeline completo funciona desde la recolección de fuentes hasta la exportación de productos finales. 8 pasos + 6 verificaciones de calidad.

---

## 8 Pasos A→B→Z Verificación

### Paso 1: Environment Setup
**Qué verificar**:
- Python 3.11+ disponible
- pip install requirements.txt funciona
- Playwright browsers installable
- System deps: texlive, ffmpeg, pandoc

**Cómo verificar**:
```bash
python3 --version
pip install -r requirements.txt -q
playwright install chromium --with-deps
which pdflatex   # or: which xelatex
which ffmpeg
which pandoc
```

**Expected result**: All commands succeed.

---

### Paso 2: Source Collection (YouTube)
**Qué verificar**:
- YouTube API key works
- Can search for videos about a topic
- Returns relevant results with metadata (title, url, channel, views, duration)

**Cómo verificar**:
```bash
# Use a test topic
export YOUTUBE_API_KEY="your_key"
python -c "
from lib.source_collector import search_videos
results = search_videos('Dan Martell scaling up', max_results=3)
print(f'Found: {len(results)} videos')
for r in results:
    print(f' - {r[\"title\"]} | {r[\"url\"]} | {r[\"channel\"]} | {r[\"view_count\"]} views')
"
```

**Expected**: 3+ videos returned with valid YouTube URLs.

---

### Paso 3: NotebookLM Login
**Qué verificar**:
- Browser automation can open NotebookLM
- Can login to Google account (fbscotta@gmail.com)
- Can navigate to notebooklm.google.com

**Cómo verificar**:
```bash
export GOOGLE_SESSION_COOKIE="base64_encoded_cookies"
python -c "
from lib.notebooklm_client import NotebookLMClient
client = NotebookLMClient()
client.login()
print('NotebookLM URL:', client.page.url)
print('Logged in:', 'New notebook' in client.page.content())
client.close()
"
```

**Expected**: Page loaded, "New notebook" visible, logged in.

**Note**: If 2FA is enabled, may need app-password or manual code entry.

---

### Paso 4: NotebookLM Create Notebook + Add Sources
**Qué verificar**:
- Can create a new notebook with title
- Can add YouTube URLs as sources
- Sources appear in notebook (visual check or DOM)

**Cómo verificar**:
```bash
python -c "
from lib.notebooklm_client import NotebookLMClient
client = NotebookLMClient()
client.login()
nb = client.create_notebook('Test: Como auto educarse con IA')
print('Created notebook:', nb.get('id'), nb.get('title'))
urls = ['https://www.youtube.com/watch?v=example1', 'https://www.youtube.com/watch?v=example2']
client.add_sources(nb, urls)
print('Sources added')
client.close()
"
```

**Expected**: Notebook created, sources added successfully.

---

### Paso 5: Extract Analysis from NotebookLM
**Qué verificar**:
- Can extract: summary, slides, FAQ, timeline, insights
- Content is meaningful (not empty, not error messages)

**Cómo verificar**:
```bash
python -c "
from lib.notebooklm_client import NotebookLMClient
client = NotebookLMClient()
client.login()
nb = client.create_notebook('Test Extraction')
# Add sources first, then wait for analysis
client.add_sources(nb, ['https://www.youtube.com/watch?v=example'])
import time; time.sleep(30)  # Wait for NotebookLM processing
analysis = client.extract_analysis(nb)
print('Summary length:', len(analysis.get('summary', '')))
print('Slides count:', len(analysis.get('slides', [])))
print('FAQ count:', len(analysis.get('faq', [])))
print('Timeline entries:', len(analysis.get('timeline', [])))
client.close()
"
```

**Expected**: Non-empty summary, slides array, FAQ entries, timeline entries.

---

### Paso 6: Content Generation (Docs + Slides + Infographics)
**Qué verificar**:
- Can generate markdown docs from analysis
- Can generate slides (SVG/Mermaid) from key points
- Can generate infographics from concepts

**Cómo verificar**:
```bash
python -c "
from lib.content_generator import generate_docs, generate_slides, generate_infographics
analysis = {'summary': '...', 'slides': [...], 'insights': [...]}
docs = generate_docs(analysis, lang='es')
print('Docs generated:', len(docs), 'sections')
slides = generate_slides(analysis, lang='es')
print('Slides generated:', len(slides), 'slides')
infographics = generate_infographics(analysis, lang='es')
print('Infographics generated:', len(infographics), 'images')
"
```

**Expected**: Docs with sections, slides with SVG content, infographics with SVG.

---

### Paso 7: Audio + Video Generation
**Qué verificar**:
- Can generate audio (MP3) from docs using ElevenLabs
- Audio matches expected language + voice (ES female or EN female)
- Can generate video (MP4) from slides + audio

**Cómo verificar**:
```bash
python -c "
from lib.content_generator import generate_audio, generate_video
docs_text = 'Content for audio narration here...'
audio_es = generate_audio(docs_text, lang='es', voice='female')
print('Audio ES:', audio_es.get('path'), 'duration:', audio_es.get('duration'))
audio_en = generate_audio(docs_text, lang='en', voice='female')
print('Audio EN:', audio_en.get('path'), 'duration:', audio_en.get('duration'))
video = generate_video(slides, audio_es, lang='es')
print('Video:', video.get('path'), 'duration:', video.get('duration'))
"
```

**Expected**: MP3 files with reasonable duration, MP4 video file.

---

### Paso 8: Quality Control (6 Checks)
**Qué verificar**:
- Completeness: PDF has all sections (intro, body, conclusion, appendix)
- Coherence: Sections flow logically, no contradictions
- Visual quality: Infographics referenced properly, load correctly
- Audio quality: MP3 duration matches expected narration time
- Mobile-friendly: PDF readable on phone-sized screen
- Branding consistency: Style, fonts, colors consistent across all products

**Cómo verificar**:
```bash
python -c "
from lib.quality_checker import run_all_checks
results = run_all_checks('output/test_topic/')
for check_name, result in results.items():
    status = '✅ PASS' if result['passed'] else '❌ FAIL'
    print(f'{status}: {check_name} — {result[\"message\"]}')
print(f'\nOverall: {sum(1 for r in results.values() if r[\"passed\"])}/6 passed')
"
```

**Expected**: All 6 checks pass.

---

## Unit Tests (pytest)

Located in `tests/` directory. Tested via pytest.

| Test File | What It Tests |
|-----------|---------------|
| test_source_collector.py | YouTube search API, result formatting |
| test_notebooklm_client.py | Login flow, notebook creation, source addition |
| test_content_generator.py | Markdown generation, slide generation, audio generation |
| test_pdf_designer.py | PDF compilation, mobile PDF, ePub generation |
| test_quality_checker.py | Each of the 6 checks individually |
| test_factory.py | End-to-end orchestration (mocked) |

Run via:
```bash
pytest tests/ -v
```

---

## Integration Test (End-to-End)

Full pipeline test with a simple topic. Run via:
```bash
python factory.py --topic "Dan Martell introduccion a scaling" --lang es --verify
```

Expected: All phases complete, all 6 quality checks pass, output files in output/<topic>/.

---

## Browser Automation Tests

For Playwright-based tests, use pytest-playwright:
```bash
pytest tests/test_browser.py --headed  # with visible browser for debugging
```

---

## Test Status

| Test Phase | Status | Last Run |
|-----------|--------|----------|
| 1. Environment Setup | 🔴 Not run yet | — |
| 2. Source Collection | 🔴 Not run yet | — |
| 3. NotebookLM Login | 🔴 Not run yet | — |
| 4. Create Notebook + Add Sources | 🔴 Not run yet | — |
| 5. Extract Analysis | 🔴 Not run yet | — |
| 6. Content Generation | 🔴 Not run yet | — |
| 7. Audio + Video | 🔴 Not run yet | — |
| 8. Quality Control | 🔴 Not run yet | — |
| Unit Tests | 🔴 Not written yet | — |
| Integration Test | 🔴 Not run yet | — |

---

> Updated: 2026-08-21. Tests to be written and run in Phase 2.
