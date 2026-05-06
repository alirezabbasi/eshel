#!/usr/bin/env python3
from pathlib import Path

FILES = [
    "ruleset.md",
    "docs/ruleset.md",
    "schema/AGENTS.md",
    "schema/INGEST.md",
    "schema/QUERY.md",
    "schema/LINT.md",
    "schema/TASKS.md",
    "schema/STANDARDS.md",
    "wiki/index.md",
    "wiki/project-brief.md",
    "wiki/log.md",
    "docs/development/04-memory/CURRENT_STATE.md",
    "docs/development/02-execution/KANBAN.md",
]

print("# Session Bootstrap Context\n")
for file_path in FILES:
    p = Path(file_path)
    print(f"## {file_path}")
    if not p.exists():
        print("MISSING")
    else:
        text = p.read_text(encoding="utf-8")
        if file_path.endswith("wiki/log.md"):
            print("\n".join(text.splitlines()[-120:]))
        else:
            print(text[:6000])
    print("\n---\n")
