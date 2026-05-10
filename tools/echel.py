#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

from echel.coherence import detect_drift
from echel.config import ConfigError, load_config, resolve_root_map
from echel.evidence import ensure_registry, validate_links, validate_registry
from echel.gates import run_gates
from echel.primitives import validate_decisions, validate_tasks
from echel.workspace import apply_workspace_move, plan_workspace_move


def _load(repo_root: Path):
    try:
        return load_config(repo_root)
    except ConfigError as exc:
        print(f"CONFIG_ERROR: {exc}", file=sys.stderr)
        sys.exit(2)


def cmd_start(repo_root: Path) -> int:
    cfg = _load(repo_root)
    roots = resolve_root_map(cfg, repo_root)
    print("Echel session start")
    print(f"- config: {cfg.path}")
    for k, v in roots.items():
        print(f"- ${k}: {v}")
    return 0


def cmd_doctor(repo_root: Path) -> int:
    cfg = _load(repo_root)
    code = 0

    print("## Doctor Report")
    print("\n### Primitive Validation")
    p_issues = []
    p_issues.extend(validate_tasks(sorted((repo_root / "wiki/tasks").glob("TASK-*.md"))))
    p_issues.extend(validate_decisions(sorted((repo_root / "wiki/decisions").glob("ADR-*.md"))))
    if not p_issues:
        print("- OK")
    else:
        code = max(code, 2)
        for i in p_issues:
            print(f"- {i.severity}: {i.message} [{i.source}]")

    print("\n### Evidence Registry")
    reg_path = repo_root / cfg.evidence_registry
    reg = ensure_registry(reg_path)
    r_issues = validate_registry(reg, str(reg_path))
    link_files = sorted((repo_root / "wiki/tasks").glob("TASK-*.md")) + sorted((repo_root / "wiki/decisions").glob("ADR-*.md"))
    l_issues = validate_links(link_files, reg)
    if not r_issues and not l_issues:
        print("- OK")
    else:
        code = max(code, 1)
        for i in [*r_issues, *l_issues]:
            print(f"- {i.severity}: {i.message} [{i.source}]")

    print("\n### Coherence Drift")
    drifts = detect_drift(repo_root)
    if not drifts:
        print("- OK")
    else:
        code = max(code, 1)
        for d in drifts:
            print(f"- {d.category}/{d.severity}: {d.message}")
            print(f"  source={d.source}")
            print(f"  fix={d.suggestion}")

    print("\n### Gates")
    results, errors = run_gates(repo_root, cfg)
    if errors:
        code = max(code, 2)
        for e in errors:
            print(f"- compile error: {e}")
    else:
        for res in results:
            if res.passed:
                print(f"- {res.gate_id}: PASS")
            else:
                code = max(code, 1)
                print(f"- {res.gate_id}: FAIL")
                for f in res.failures:
                    print(f"  - {f}")
    return code


def _set_task_status(path: Path, done: bool) -> None:
    text = path.read_text(encoding="utf-8")
    new_status = "status: done" if done else "status: planned"
    if re.search(r"^status:\s*\w+\s*$", text, re.MULTILINE):
        text = re.sub(r"^status:\s*\w+\s*$", new_status, text, flags=re.MULTILINE)
    else:
        text = text.replace("---\n", f"---\n{new_status}\n", 1)
    path.write_text(text, encoding="utf-8")


def _set_kanban_task(repo_root: Path, task_id: str, done: bool) -> None:
    p = repo_root / "docs/development/02-execution/KANBAN.md"
    text = p.read_text(encoding="utf-8")
    mark = "x" if done else " "
    updated, count = re.subn(rf"- \[(?: |x)\] ({re.escape(task_id)})\b", rf"- [{mark}] \1", text)
    if count == 0:
        updated += f"\n- [{'x' if done else ' '}] {task_id}\n"
    p.write_text(updated, encoding="utf-8")


def cmd_close_task(repo_root: Path, task_id: str) -> int:
    cfg = _load(repo_root)
    _ = cfg
    matches = sorted((repo_root / "wiki/tasks").glob(f"{task_id}-*.md"))
    if not matches:
        print(f"task not found: {task_id}", file=sys.stderr)
        return 2
    task_path = matches[0]
    text = task_path.read_text(encoding="utf-8")
    evid_links = re.findall(r"\bEVID-[A-Z0-9\-]{3,}\b", text)
    if not evid_links:
        print("close-task blocked: task must reference at least one evidence ID", file=sys.stderr)
        return 1

    reg = ensure_registry(repo_root / cfg.evidence_registry)
    unknown = sorted({e for e in evid_links if e not in reg.get("artifacts", {})})
    if unknown:
        print(f"close-task blocked: unknown evidence IDs: {', '.join(unknown)}", file=sys.stderr)
        return 1

    _set_task_status(task_path, done=True)
    _set_kanban_task(repo_root, task_id, done=True)
    print(f"closed {task_id}")
    return 0


def _sync_last_updated(path: Path, target_date: str) -> None:
    text = path.read_text(encoding="utf-8")
    if re.search(r"^Last updated:\s*", text, re.MULTILINE):
        out = re.sub(r"^Last updated:\s*.*$", f"Last updated: {target_date}", text, flags=re.MULTILINE)
    else:
        out = text.rstrip() + f"\n\nLast updated: {target_date}\n"
    path.write_text(out, encoding="utf-8")


def cmd_sync_memory(repo_root: Path) -> int:
    today = date.today().isoformat()
    targets = [
        repo_root / "docs/development/04-memory/WHERE_ARE_WE.md",
        repo_root / "docs/development/04-memory/CURRENT_STATE.md",
    ]
    for p in targets:
        if p.exists():
            _sync_last_updated(p, today)
    print(f"memory synced to {today}")
    return 0


def cmd_workspace_move(repo_root: Path, dry_run: bool) -> int:
    cfg = _load(repo_root)
    if dry_run:
        changes = plan_workspace_move(repo_root, cfg)
        print("workspace move dry-run")
        print(f"- files to rewrite: {len(changes)}")
        for c in changes[:50]:
            print(f"- {c.path} ({c.before_hash} -> {c.after_hash})")
        if len(changes) > 50:
            print(f"- ... and {len(changes) - 50} more")
        return 0

    manifest = apply_workspace_move(repo_root, cfg)
    print(f"workspace move applied, rollback manifest: {manifest}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="echel")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("start")
    sub.add_parser("doctor")

    close = sub.add_parser("close-task")
    close.add_argument("task_id")

    sub.add_parser("sync-memory")

    ws = sub.add_parser("workspace")
    ws_sub = ws.add_subparsers(dest="workspace_cmd", required=True)
    move = ws_sub.add_parser("move")
    mode = move.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path.cwd()

    if args.cmd == "start":
        return cmd_start(root)
    if args.cmd == "doctor":
        return cmd_doctor(root)
    if args.cmd == "close-task":
        return cmd_close_task(root, args.task_id)
    if args.cmd == "sync-memory":
        return cmd_sync_memory(root)
    if args.cmd == "workspace" and args.workspace_cmd == "move":
        dry_run = True if args.dry_run or not args.apply else False
        return cmd_workspace_move(root, dry_run=dry_run)

    print("unknown command", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
