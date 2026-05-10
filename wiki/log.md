---
type: log
status: active
---
# Log

## [2026-05-06] scaffold | echel baseline
- Established domain-agnostic Echel scaffold.
- Added governance, memory, and execution control artifacts.
- Hardened workflow automation and knowledge quality gates.

## [2026-05-06] model | project intelligence compounding
- Added a canonical model for intelligence and memory compounding in `wiki/systems/project-intelligence-compounding-model.md`.
- Defined delivery, reliability, and strategy loops with bug-management and RCA feedback paths.
- Added maturity stages, operating cadence, decision guidance protocol, and measurement model for direction shaping.

## [2026-05-08] architecture | four-layer os
- Defined Echel as a four-layer operating system: Knowledge OS, Execution OS, Evidence OS, and Automation OS.
- Added v1 architecture and contract docs covering lifecycle states, typed task graph, artifact registry, proof packs, and deterministic gate running.
- Updated execution and memory artifacts so rollout is traceable and operationally visible.

## [2026-05-10] repo-model | target-root-with-internal-echel-core
- Clarified generated project topology: target software repository is the root artifact, with Echel relocated under `echel-core/`.
- Updated guidance so implementation happens at target project root while orchestration remains in `echel-core`.
- Recorded decision to keep `echel-core` out of target-project Git history via `.gitignore`.

## [2026-05-11] release-2 | v2-mvp-foundation
- Added declarative `project.echel` contract loading and validation.
- Added path abstraction roots and migration-map rewrite support with dry-run/apply workspace move flow and rollback manifests.
- Added `echel` core commands: `start`, `doctor`, `close-task`, and `sync-memory`.
- Added coherence drift checks, evidence registry validation/linkage checks, and compiled gate policy execution.
