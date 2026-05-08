# Deterministic Gate Runner Contract (v1)

## Objective

Provide a deterministic mechanism for evaluating whether a task or release can close.

## Gate taxonomy

- `knowledge_gate`: required docs/wiki/decision artifacts are current.
- `execution_gate`: lifecycle/state/dependency rules are satisfied.
- `evidence_gate`: required proof artifacts are present and valid.
- `quality_gate`: tests/lint/checks meet configured thresholds.
- `release_gate`: release-specific readiness checks pass.

## Evaluation order

1. Knowledge gate
2. Execution gate
3. Evidence gate
4. Quality gate
5. Release gate (only when applicable)

## Determinism constraints

- Same inputs must produce identical verdicts.
- Non-deterministic external calls are forbidden unless captured as immutable artifacts first.
- Gate definitions must be versioned and referenced in outputs.

## Failure semantics

- `fail`: gate evaluated and requirements not met.
- `blocked`: gate cannot evaluate due to missing required inputs.

Both outcomes must include explicit remediation hints.
