# A2A Fixes — Fixes aplicados al sistema

> Registro de fixes aplicados para resolver bugs y otros problemas en AIIA-NTBLM-Factory.
> Updated: 2026-08-21. All times UTC-3.

---

## Fix History

### FIX-001: A2A file structure gap
- **Date**: 2026-08-21
- **Issue**: A2A files missing (only Quickstart + WIP created initially)
- **Fix**: Created remaining A2A files:
  - A2A-Technical.md
  - A2A-WHAT.md
  - A2A-Blockers.md
  - A2A-Bugs.md
  - A2A-Fixes.md
  - A2A-Analysis.md
  - A2A-Tests.md
  - A2A-Production-Metadata.md
- **Status**: ✅ Fixed

### FIX-002: Factory structure missing
- **Date**: 2026-08-21
- **Issue**: No factory.py, no lib/, no config.product.json
- **Fix**: Created factory.py + config.product.json + lib/container structure
- **Status**: ✅ Fixed

### FIX-003: Environment variables not documented
- **Date**: 2026-08-21
- **Issue**: README+skills didn't list all required env vars
- **Fix**: Added .env.example with all env vars documented
- **Status**: ✅ Fixed

### FIX-004: Dependency list missing
- **Date**: 2026-08-21
- **Issue**: No requirements.txt for Python dependencies
- **Fix**: Created requirements.txt with all needed packages
- **Status**: ✅ Fixed

### FIX-005: Factory constellation gap for NTBLM workflow
- **Date**: 2026-08-21
- **Issue**: Factory didn't account for NotebookLM browser-based workflow (no API, must use Playwright)
- **Fix**: Added notebooklm_client.py, updated factory.py to route through browser automation layer, added BLO-01 + BLO-07 blockers with workarounds
- **Status**: ✅ Fixed

---

## Pending Fixes (to be applied when bugs are resolved)

See A2A-Bugs.md for open bugs. Each fix below will be recorded here once applied.

| Bug ID | Expected Fix Approach | Status |
|--------|----------------------|--------|
| BUG-01 | Adaptive selectors + retry in notebooklm_client.py | Pending |
| BUG-02 | Voice verification + fallback in content_generator.py | Pending |
| BUG-03 | Relevance filtering in source_collector.py | Pending |
| BUG-04 | LaTeX content sanitization in pdf_designer.py | Pending |
| BUG-05 | Duration estimation in content_generator.py | Pending |

---

## Fix Workflow

Every fix:
1. Recorded here (A2A-Fixes.md) with date + issue + resolution
2. Bug closed in A2A-Bugs.md
3. Related blocker closed in A2A-Blockers.md if applicable
4. Code updated in the relevant module

---

> Updated: 2026-08-21. Next review: after first bug is resolved.
