# A2A Bugs — Registro de bugs

> Bugs encontrados en AIIA-NTBLM-Factory o en sus dependencias.
> Updated: 2026-08-21. All times UTC-3.

---

## Bugs Activos

### [REPORTED] BUG-01: NotebookLM UI may change, breaking Playwright selectors
- **Severity**: Medium
- **Component**: notebooklm_client.py
- **Description**: Google may update NotebookLM UI periodically. CSS/Tag selectors used by Playwright may break.
- **Impact**: Browser automation fails — cannot add sources, extract analysis
- **Fix approach**:
  - Use robust selectors: aria-labels, role attributes, text content matching (less brittle than CSS class names)
  - Add retry logic with alternative selectors
  - Monitor Google release notes / send alerts on failure
- **Status**: Open — will handle with adaptive selectors + retry

### [REPORTED] BUG-02: ElevenLabs voice gender mismatch
- **Severity**: Low
- **Component**: content_generator.py
- **Description**: ElevenLabs voice selection may not match requested gender if voice ID is not available in a specific accent
- **Impact**: Audio may sound male even when female requested
- **Fix approach**:
  - Verify voice ID before TTS call: list voices, filter by gender + accent
  - Fallback voice if preferred not available
- **Status**: Open — will handle with voice verification step

### [REPORTED] BUG-03: YouTube search may return irrelevant videos
- **Severity**: Medium
- **Component**: source_collector.py
- **Description**: YouTube API relevance ranking may return off-topic results
- **Impact**: NotebookLM analysis will have noisy source material
- **Fix approach**:
  - Add relevance filtering: keyword matching + channel verification (must be Dan Martell's channel or related authoritative channels)
  - Manual curation step: owner reviews and approves sources before NotebookLM analysis
- **Status**: Open — filtering TBD

### [REPORTED] BUG-04: PDF generation may fail with long content
- **Severity**: Medium
- **Component**: pdf_designer.py
- **Description**: LaTeX may fail to compile if content has special characters or is very long
- **Impact**: PDF not generated
- **Fix approach**:
  - Sanitize content before LaTeX compilation (escape special chars)
  - Split long content into multiple compilations
  - Use robust LaTeX template with proper escaping
- **Status**: Open — will test with long content

### [REPORTED] BUG-05: Audio duration mismatch
- **Severity**: Low
- **Component**: content_generator.py
- **Description**: ElevenLabs TTS duration may not match expected page count
- **Impact**: Audio may be too short/long for the content
- **Fix approach**:
  - Estimate word count → expected duration (words/min for TTS)
  - Adjust TTS speed if needed (ElevenLabs supports stability + similarity boost)
- **Status**: Open — will handle with duration estimation

---

## Fixed Bugs (already resolved)

| ID | Issue | Fix |
|----|-------|-----|
| BUG-FIXED-1 | A2A file structure missing | All A2A files created |
| BUG-FIXED-2 | Factory structure missing | factory.py + config + lib/ structure in place |
| BUG-FIXED-3 | No Google API identified | YouTube API key identified and ready to use |

---

## Bug Triage Status

| Bug | Severity | Priority | Owner | Target Fix |
|-----|----------|----------|-------|------------|
| BUG-01 | Medium | High | AIIA | Before first NotebookLM use |
| BUG-02 | Low | Medium | AIIA | Before first audio generation |
| BUG-03 | Medium | High | AIIA | Before first NotebookLM source add |
| BUG-04 | Medium | High | AIIA | Before first PDF generation |
| BUG-05 | Low | Low | AIIA | Later phase |

---

> Updated: 2026-08-21. Next review: after first end-to-end test.
