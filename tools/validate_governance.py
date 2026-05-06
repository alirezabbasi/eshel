#!/usr/bin/env python3
from pathlib import Path
import sys

required = [
    "ruleset.md",
    "docs/ruleset.md",
    "docs/development/README.md",
    "docs/development/02-execution/KANBAN.md",
    "docs/development/04-memory/CURRENT_STATE.md",
    "docs/development/04-memory/SESSION_LEDGER.md",
    "docs/development/04-memory/DECISION_LOG.md",
    "docs/development/04-memory/RISKS_AND_ASSUMPTIONS.md",
    "docs/development/debugging/debugcmd.md",
]

missing = [p for p in required if not Path(p).exists()]
if missing:
    print("Missing governance artifacts:")
    for m in missing:
        print(f"- {m}")
    sys.exit(2)

print("Governance artifacts validated")
sys.exit(0)
