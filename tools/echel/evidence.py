from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import re

EVIDENCE_LINK_PATTERN = re.compile(r"\b(EVID-[A-Z0-9\-]{3,})\b")


@dataclass
class EvidenceIssue:
    severity: str
    source: str
    message: str


def ensure_registry(path: Path) -> dict:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 1, "artifacts": {}}
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return data
    return json.loads(path.read_text(encoding="utf-8"))


def validate_registry(registry: dict, source: str) -> list[EvidenceIssue]:
    issues: list[EvidenceIssue] = []
    if not isinstance(registry, dict):
        return [EvidenceIssue("critical", source, "evidence registry must be object")]
    if registry.get("version") != 1:
        issues.append(EvidenceIssue("critical", source, "registry version must equal 1"))
    artifacts = registry.get("artifacts")
    if not isinstance(artifacts, dict):
        issues.append(EvidenceIssue("critical", source, "artifacts must be mapping"))
        return issues
    for evid, payload in artifacts.items():
        if not EVIDENCE_LINK_PATTERN.fullmatch(evid):
            issues.append(EvidenceIssue("critical", source, f"invalid evidence id '{evid}'"))
        if not isinstance(payload, dict):
            issues.append(EvidenceIssue("major", source, f"artifact '{evid}' payload must be object"))
            continue
        if "path" not in payload:
            issues.append(EvidenceIssue("major", source, f"artifact '{evid}' missing path"))
    return issues


def extract_evidence_links(text: str) -> set[str]:
    return set(EVIDENCE_LINK_PATTERN.findall(text))


def validate_links(files: list[Path], registry: dict) -> list[EvidenceIssue]:
    artifacts = registry.get("artifacts", {}) if isinstance(registry, dict) else {}
    known = set(artifacts.keys())
    issues: list[EvidenceIssue] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for evid in sorted(extract_evidence_links(text)):
            if evid not in known:
                issues.append(EvidenceIssue("major", str(path), f"references unknown evidence id {evid}"))
    return issues
