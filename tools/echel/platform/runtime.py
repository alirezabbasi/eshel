from __future__ import annotations

import json
from pathlib import Path


PLATFORM_CONFIG = Path('.echel/platform/config.json')

DEFAULT_CONFIG = {
    'version': 1,
    'host': '127.0.0.1',
    'port': 8787,
    'db_path': '.echel/platform/platform.db',
}


def ensure_platform_config(repo_root: Path) -> Path:
    cfg_path = repo_root / PLATFORM_CONFIG
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    if not cfg_path.exists():
        cfg_path.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + '\n', encoding='utf-8')
    return cfg_path


def load_platform_config(repo_root: Path) -> dict:
    path = ensure_platform_config(repo_root)
    raw = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(raw, dict):
        raise ValueError('platform config must be a JSON object')
    return raw
