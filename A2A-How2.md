# A2A-How2.md

<!-- AIIA-FACTORY-PERIODIC-UPDATE -->
## AIIA Factory Periodic Update (injected 2026-08-22)

When resuming this repo as part of an AIIA Factory batch pass, in addition to stamping
`A2A-*.md` / `README.md`, the next AI agent MUST also update the machine-readable state:

1. `.aiia/factory.manifest.json` — refresh the `factory_verification` block
   (`last_verified_date`, `task_group`, `status`, `summary`).
2. `.aiia/logs/factory-verification-YYYY-MM-DD.jsonl` — append one JSON event line
   `{"event":"factory_verification","date":"...","task_group":"...","repo":"...","status":"..."}`.
3. Do NOT force-push. If `git push` is rejected non-fast-forward, run `git fetch origin`
   then `git rebase origin/main` (or reset --hard to origin/main for doc-only stamps) and re-push.
4. See the control plane: `/home/fb/Downloads/A2A-SHARED-PROGRESS.md`.
