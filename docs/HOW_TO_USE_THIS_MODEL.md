# How to Use Echel to Drive Development

## How to Start with Echel

Echel works best when you use it with three things together:

- an LLM coding tool (`Codex`, `Claude Code`, `Cursor`, or similar)
- `Obsidian` (as the project knowledge interface)
- a curious mind (you drive questions, exploration, and decisions)

### 1) Run the Echel wizard

```bash
make init-wizard
```

The wizard collects the minimum essential information to initialize:

- project mission and boundaries
- architecture references and decision policy
- execution standards and task structure
- governance, memory, and quality-gate controls

### 2) Validate the initialization

```bash
make wiki-health
```

This verifies that generated artifacts, links, and governance controls are consistent and ready.

### 3) Open the wiki in Obsidian

Open `wiki/` as an Obsidian vault.

Echel generates linked Markdown (`[[wikilinks]]`) so project relationships are visible in Obsidian's graph and remain navigable as the system grows.

### 4) Start development with your LLM coding tool

Use your coding assistant (Codex, Claude Code, Cursor, etc.) to:

1. read project context from the wiki
2. pick or create a task artifact
3. implement with verification
4. update linked knowledge artifacts
5. append the session log

### 5) Work in a compounding loop

The development loop is:

`idea -> structured knowledge -> task -> implementation -> verification -> updated knowledge`

Echel is designed so code and understanding evolve together, not separately.

## Daily loop
1. Run `make session-bootstrap`.
2. Run `make wrw` whenever you need a concise "Where Are We?" status snapshot.
3. Select one task from `wiki/tasks/`.
4. Implement smallest safe change with tests.
5. Update canonical wiki pages and task status.
6. Run `make wiki-health`.
7. Sync `docs/development` memory and execution docs.
8. Commit changes with clear scope.
