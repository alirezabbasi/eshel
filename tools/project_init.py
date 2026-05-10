#!/usr/bin/env python3
import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

CORE_ITEMS = [
    "assets",
    "docs",
    "prompts",
    "raw",
    "schema",
    "tools",
    "wiki",
    "LICENSE",
    "ruleset.md",
    "README.md",
    "Makefile",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Project/workspace name")
    parser.add_argument("--mode", choices=["scratch", "existing"], required=True)
    parser.add_argument("--source", help="Path to existing codebase (required for existing mode)")
    parser.add_argument(
        "--dest",
        default=".",
        help="Destination parent directory where the new workspace will be created",
    )
    return parser.parse_args()


def copy_core_template(repo_root: Path, echel_core_dir: Path) -> None:
    echel_core_dir.mkdir(parents=True, exist_ok=False)
    for item in CORE_ITEMS:
        src = repo_root / item
        dst = echel_core_dir / item
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def copy_existing_source(source_dir: Path, workspace_dir: Path) -> None:
    shutil.copytree(
        source_dir,
        workspace_dir,
        ignore=shutil.ignore_patterns(".git", "echel-core"),
    )


def ensure_workspace_gitignore(workspace_dir: Path) -> None:
    gitignore_path = workspace_dir / ".gitignore"
    required_line = "echel-core/"
    if gitignore_path.exists():
        current = gitignore_path.read_text(encoding="utf-8")
        if required_line not in current.splitlines():
            suffix = "" if current.endswith("\n") else "\n"
            gitignore_path.write_text(
                current
                + f"{suffix}\n# Keep Echel framework out of project repository\n{required_line}\n",
                encoding="utf-8",
            )
        return

    gitignore_path.write_text(
        "# Keep Echel framework out of project repository\n"
        "echel-core/\n"
        "\n"
        "# Common local artifacts\n"
        ".DS_Store\n"
        "__pycache__/\n"
        "*.pyc\n",
        encoding="utf-8",
    )


def write_project_identity_files(workspace_dir: Path, project_name: str, mode: str, source: str | None) -> None:
    readme_path = workspace_dir / "README.md"
    license_path = workspace_dir / "LICENSE"

    if readme_path.exists():
        return

    lines = [
        f"# {project_name}",
        "",
        "This is the software project repository initialized by Echel.",
        "",
        "## Structure",
        "",
        "- `./`: Project codebase and repository root",
        "- `./echel-core/`: Internal Echel framework for governance and workflow orchestration",
        "",
        "## Next steps",
        "",
        "1. Start implementing software in this repository root.",
        "2. Use `./echel-core` for governance and knowledge workflows.",
        "3. Keep `echel-core/` ignored by this repository's Git history.",
        "",
        f"Initialization mode: `{mode}`",
    ]
    if source:
        lines.append(f"Source path: `{source}`")
    lines.append("")
    readme_path.write_text("\n".join(lines), encoding="utf-8")

    if not license_path.exists():
        license_path.write_text(
            "Copyright (c) "
            f"{datetime.now(timezone.utc).year} {project_name}\n\n"
            "All rights reserved.\n",
            encoding="utf-8",
        )


def update_core_context(echel_core_dir: Path, project_name: str, mode: str, source: str | None) -> None:
    brief = echel_core_dir / "wiki" / "project-brief.md"
    if brief.exists() and "# Project Brief" in brief.read_text(encoding="utf-8"):
        brief.write_text(
            brief.read_text(encoding="utf-8").replace(
                "# Project Brief", f"# Project Brief - {project_name}", 1
            ),
            encoding="utf-8",
        )

    log = echel_core_dir / "wiki" / "log.md"
    stamp = datetime.now(timezone.utc).date()
    with log.open("a", encoding="utf-8") as f:
        f.write(
            f"\n## [{stamp}] init | {project_name}\n"
            f"- Initialized project in `{mode}` mode.\n"
            f"- Generated project-root workspace with internal `echel-core/` orchestration.\n"
        )
        if source:
            f.write(f"- Source path: `{source}`.\n")


def main() -> int:
    args = parse_args()
    if args.mode == "existing" and not args.source:
        raise SystemExit("--source is required when --mode=existing")

    repo_root = Path(__file__).resolve().parents[1]
    dest_parent = Path(args.dest).resolve()
    workspace_dir = dest_parent / args.name
    source_dir = Path(args.source).resolve() if args.source else None

    if workspace_dir.exists():
        raise SystemExit(f"Target workspace already exists: {workspace_dir}")
    if args.mode == "existing":
        if source_dir is None or not source_dir.is_dir():
            raise SystemExit(f"Invalid --source path: {args.source}")

    echel_core_dir = workspace_dir / "echel-core"

    if args.mode == "existing":
        copy_existing_source(source_dir, workspace_dir)
    else:
        workspace_dir.mkdir(parents=True, exist_ok=False)

    copy_core_template(repo_root, echel_core_dir)
    ensure_workspace_gitignore(workspace_dir)
    write_project_identity_files(workspace_dir, args.name, args.mode, args.source)
    update_core_context(echel_core_dir, args.name, args.mode, args.source)

    print(f"Initialized workspace: {workspace_dir}")
    print(f"- Echel framework: {echel_core_dir}")
    print(f"- Project repository root: {workspace_dir}")
    print("Next:")
    print(f"  cd {workspace_dir} && git init")
    print(f"  cd {workspace_dir}/echel-core && make session-bootstrap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
