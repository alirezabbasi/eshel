from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Iterable
import uuid


MEMORY_FILE = Path('.echel/memory_records.jsonl')


@dataclass
class MemoryRecord:
    record_id: str
    ts: str
    record_type: str
    title: str
    links: list[str]
    contradiction: bool
    payload: dict


def _now() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def ensure_memory_store(repo_root: Path) -> Path:
    p = repo_root / MEMORY_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text('', encoding='utf-8')
    return p


def append_record(
    repo_root: Path,
    record_type: str,
    title: str,
    links: list[str],
    contradiction: bool,
    payload: dict,
) -> MemoryRecord:
    store = ensure_memory_store(repo_root)
    rec = MemoryRecord(
        record_id=f"MEM-{uuid.uuid4().hex[:10].upper()}",
        ts=_now(),
        record_type=record_type,
        title=title,
        links=links,
        contradiction=contradiction,
        payload=payload,
    )
    with store.open('a', encoding='utf-8') as f:
        f.write(json.dumps(asdict(rec), sort_keys=True) + '\n')
    return rec


def read_records(repo_root: Path) -> list[MemoryRecord]:
    store = ensure_memory_store(repo_root)
    out: list[MemoryRecord] = []
    for line in store.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        out.append(MemoryRecord(**raw))
    return sorted(out, key=lambda r: r.ts)


def query_records(
    repo_root: Path,
    record_type: str | None = None,
    contradiction_only: bool = False,
    text: str | None = None,
) -> list[MemoryRecord]:
    records = read_records(repo_root)
    results: list[MemoryRecord] = []
    needle = (text or '').lower().strip()
    for rec in records:
        if record_type and rec.record_type != record_type:
            continue
        if contradiction_only and not rec.contradiction:
            continue
        if needle:
            blob = ' '.join([rec.title, json.dumps(rec.payload, sort_keys=True), ' '.join(rec.links)]).lower()
            if needle not in blob:
                continue
        results.append(rec)
    return results


def contradiction_summary(records: Iterable[MemoryRecord]) -> dict:
    recs = list(records)
    total = len(recs)
    contradictions = sum(1 for r in recs if r.contradiction)
    return {
        'total': total,
        'contradictions': contradictions,
        'ratio': round((contradictions / total), 3) if total else 0.0,
    }
