# Eshel Governance Ruleset

This file extends `ruleset.md` with operational controls.

## Documentation and Memory Controls

- Keep `wiki/index.md` and `wiki/log.md` current.
- Maintain memory artifacts:
  - `docs/development/04-memory/CURRENT_STATE.md`
  - `docs/development/04-memory/SESSION_LEDGER.md`
  - `docs/development/04-memory/DECISION_LOG.md`
  - `docs/development/04-memory/RISKS_AND_ASSUMPTIONS.md`

## Execution Controls

- Execution tracking lives in `docs/development/02-execution/KANBAN.md`.
- Task statuses must match evidence in wiki and development memory docs.
- Non-completed tasks require explicit Definition of Done.

## Debugging Controls

- Register every discovered bug in `docs/development/debugging/BUG-00001.md` style.
- Log development/debug commands in `docs/development/debugging/debugcmd.md` with timestamp, command, purpose, and status.

## Status Protocol

`wrw` is the dedicated "Where Are We?" shortcut command for rapid status.

When asked "Where are we?" (or when running `make wrw`), answer with exactly:

- Completed
- Recent
- Current
- Next
- Risks/Blocks

Source that answer from current state, session ledger, and kanban documents.
Keep `docs/development/04-memory/WHERE_ARE_WE.md` synchronized as the concise snapshot artifact for this protocol.
