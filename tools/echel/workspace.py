from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import shutil
import json

from .config import ProjectConfig, apply_migration_map

TEXT_EXTS = {".md", ".txt", ".py", ".json", ".echel", ".yml", ".yaml", ".toml", ".mk", ".sh"}


@dataclass
class RewriteChange:
    path: str
    before_hash: str
    after_hash: str


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _candidate_files(root: Path) -> list[Path]:
    files = []
    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in {".git", ".venv", "__pycache__"}:
                continue
            continue
        if p.suffix.lower() in TEXT_EXTS:
            files.append(p)
    return files


def plan_workspace_move(repo_root: Path, cfg: ProjectConfig) -> list[RewriteChange]:
    changes: list[RewriteChange] = []
    for path in _candidate_files(repo_root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rewritten = apply_migration_map(text, cfg)
        if rewritten != text:
            changes.append(
                RewriteChange(
                    path=str(path.relative_to(repo_root)),
                    before_hash=_hash(text),
                    after_hash=_hash(rewritten),
                )
            )
    return changes


def write_impact_preview(repo_root: Path, changes: list[RewriteChange]) -> Path:
    preview_path = repo_root / ".echel" / "workspace_move_impact.json"
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "files_to_rewrite": len(changes),
        "changes": [c.__dict__ for c in changes],
    }
    preview_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return preview_path


def apply_workspace_move(repo_root: Path, cfg: ProjectConfig) -> Path:
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    roll_root = repo_root / ".echel" / "rollback" / ts
    backup_root = roll_root / "backup"
    backup_root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "version": 1,
        "created_at": ts,
        "changes": [],
    }

    for path in _candidate_files(repo_root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rewritten = apply_migration_map(text, cfg)
        if rewritten == text:
            continue
        rel = path.relative_to(repo_root)
        backup_path = backup_root / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        path.write_text(rewritten, encoding="utf-8")
        manifest["changes"].append(
            {
                "path": str(rel),
                "backup": str(backup_path.relative_to(repo_root)),
                "before_hash": _hash(text),
                "after_hash": _hash(rewritten),
            }
        )

    man_path = roll_root / "manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return man_path
