from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path('.echel/llm_contracts.json')


def ensure_contracts(repo_root: Path) -> dict:
    p = repo_root / CONTRACT_PATH
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'version': 1,
            'states': ['plan', 'implement', 'review'],
            'transitions': {
                'plan': ['implement'],
                'implement': ['review'],
                'review': ['implement'],
            },
            'guards': {
                'review': ['doctor_pass'],
            },
        }
        p.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        return data
    return json.loads(p.read_text(encoding='utf-8'))


def validate_transition(contract: dict, current: str, target: str, doctor_pass: bool) -> tuple[bool, str]:
    transitions = contract.get('transitions', {})
    allowed = transitions.get(current, [])
    if target not in allowed:
        return False, f'transition {current} -> {target} is not allowed'
    guards = contract.get('guards', {}).get(target, [])
    if 'doctor_pass' in guards and not doctor_pass:
        return False, f'transition {current} -> {target} blocked: doctor must pass'
    return True, 'allowed'
