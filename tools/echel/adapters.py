from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RuntimeAdapter:
    name: str
    detect_files: list[str]
    task_hook: str
    evidence_hook: str


ADAPTERS = [
    RuntimeAdapter(
        name='python',
        detect_files=['pyproject.toml', 'requirements.txt'],
        task_hook='python3 -m py_compile tools/*.py',
        evidence_hook='python3 tools/echel.py doctor',
    ),
    RuntimeAdapter(
        name='typescript',
        detect_files=['tsconfig.json', 'package.json'],
        task_hook='npm run -s lint',
        evidence_hook='npm test --silent',
    ),
]


def detect_adapters(repo_root: Path) -> list[RuntimeAdapter]:
    available: list[RuntimeAdapter] = []
    for adapter in ADAPTERS:
        if any((repo_root / marker).exists() for marker in adapter.detect_files):
            available.append(adapter)
    return available
