#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--name", required=True)
parser.add_argument("--mode", choices=["scratch", "existing"], required=True)
parser.add_argument("--source")
args = parser.parse_args()

Path("raw/sources").mkdir(parents=True, exist_ok=True)
Path("raw/codebase").mkdir(parents=True, exist_ok=True)
Path("wiki/sessions").mkdir(parents=True, exist_ok=True)

brief = Path("wiki/project-brief.md")
if brief.exists() and "# Project Brief" in brief.read_text(encoding="utf-8"):
    brief.write_text(
        brief.read_text(encoding="utf-8").replace(
            "# Project Brief", f"# Project Brief - {args.name}", 1
        ),
        encoding="utf-8",
    )

log = Path("wiki/log.md")
stamp = datetime.now(timezone.utc).date()
with log.open("a", encoding="utf-8") as f:
    f.write(
        f"\n## [{stamp}] init | {args.name}\n"
        f"- Initialized project in `{args.mode}` mode.\n"
    )
    if args.source:
        f.write(f"- Source path: `{args.source}`.\n")

print(f"Initialized {args.name} in {args.mode} mode")
