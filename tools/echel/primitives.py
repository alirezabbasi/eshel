from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

ID_PATTERNS = {
    "task": re.compile(r"^TASK-\d{4}$"),
    "decision": re.compile(r"^ADR-\d{4}$"),
    "evidence": re.compile(r"^EVID-[A-Z0-9\-]{3,}$"),
    "gate": re.compile(r"^GATE-[A-Z0-9\-]{3,}$"),
    "handoff": re.compile(r"^HANDOFF-[A-Z0-9\-]{3,}$"),
}


@dataclass
class PrimitiveIssue:
    severity: str
    source: str
    message: str


def _extract_h1(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _task_id_from_name(path: Path) -> str | None:
    m = re.match(r"(TASK-\d{4})-", path.name)
    if m:
        return m.group(1)
    return None


def validate_tasks(task_files: Iterable[Path]) -> list[PrimitiveIssue]:
    issues: list[PrimitiveIssue] = []
    seen: set[str] = set()
    for task in task_files:
        task_id = _task_id_from_name(task)
        if not task_id:
            issues.append(PrimitiveIssue("critical", str(task), "invalid task filename format"))
            continue
        if task_id in seen:
            issues.append(PrimitiveIssue("critical", str(task), f"duplicate task id {task_id}"))
        seen.add(task_id)
        if not ID_PATTERNS["task"].match(task_id):
            issues.append(PrimitiveIssue("critical", str(task), f"invalid task id {task_id}"))

        text = task.read_text(encoding="utf-8")
        h1 = _extract_h1(text)
        if task_id not in h1:
            issues.append(PrimitiveIssue("major", str(task), "task heading does not include task ID"))
        if "## Definition of Done" not in text:
            issues.append(PrimitiveIssue("critical", str(task), "missing Definition of Done section"))

    return issues


def validate_decisions(decision_files: Iterable[Path]) -> list[PrimitiveIssue]:
    issues: list[PrimitiveIssue] = []
    seen: set[str] = set()
    for decision in decision_files:
        m = re.search(r"(ADR-\d{4})", decision.name)
        if not m:
            issues.append(PrimitiveIssue("major", str(decision), "decision file missing ADR ID in filename"))
            continue
        decision_id = m.group(1)
        if decision_id in seen:
            issues.append(PrimitiveIssue("critical", str(decision), f"duplicate decision id {decision_id}"))
        seen.add(decision_id)
        if not ID_PATTERNS["decision"].match(decision_id):
            issues.append(PrimitiveIssue("critical", str(decision), f"invalid decision id {decision_id}"))
    return issues


def validate_gate_ids(gate_ids: Iterable[str], source: str) -> list[PrimitiveIssue]:
    issues: list[PrimitiveIssue] = []
    for gate_id in gate_ids:
        if not ID_PATTERNS["gate"].match(gate_id):
            issues.append(PrimitiveIssue("critical", source, f"invalid gate id {gate_id}"))
    return issues
