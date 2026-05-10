# Debug Command Log

| Timestamp (UTC) | Command | Purpose | Status |
|---|---|---|---|
| 2026-05-06T00:00:00Z | seed | initialize log format | success |
| 2026-05-08T11:40:15Z | `rg -n --hidden --glob '!.git' 'Eshel|eshel|ESHEL'` | verify naming consistency and scan references before architecture edits | success |
| 2026-05-08T11:40:15Z | `sed -n '1,220p' ruleset.md` | reload top-priority project rules before planning/editing | success |
| 2026-05-08T11:40:15Z | `sed -n '1,260p' docs/ruleset.md` | validate stricter operational controls prior to implementation | success |
| 2026-05-08T11:40:15Z | `git status --short` | verify modified/new files after four-layer architecture rollout | success |
| 2026-05-10T20:47:23Z | `python3 tools/project_init.py --name echel_scratch_test --mode scratch --dest /tmp` | verify generated workspace uses project-root model with internal `echel-core/` | success |
| 2026-05-10T20:47:23Z | `python3 tools/project_init.py --name echel_existing_test --mode existing --dest /tmp --source /tmp/echel_existing_src` | verify existing-repo import plus root `.gitignore` injection for `echel-core/` | success |
| 2026-05-10T20:47:23Z | `make wiki-health` | run required quality and governance gates after generator/template changes | success |
