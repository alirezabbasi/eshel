# Echel Workspace

This repository now uses a split architecture:

- `echel-core/`: the Echel framework, governance, schemas, tools, prompts, and base scaffold template.
- `<project-name>/` (generated): software projects initialized and managed through Echel, each in its own dedicated folder.

## Why this split

Echel is documentation- and governance-heavy by design. Real software projects should not share the same top-level hierarchy as framework internals. This separation keeps platform evolution and product delivery cleanly isolated.

## Quick start

```bash
make session-bootstrap
make init-wizard
```

Or non-interactive:

```bash
make init-project NAME=my-project MODE=scratch
```

For framework details, see [echel-core/README.md](echel-core/README.md).
