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


def write_workspace_gitignore(workspace_dir: Path) -> None:
    (workspace_dir / ".gitignore").write_text(
        "# Keep Echel framework out of project repository\n"
        "echel-core/\n"
        "\n"
        "# Common local artifacts\n"
        ".DS_Store\n"
        "__pycache__/\n"
        "*.pyc\n",
        encoding="utf-8",
    )


def write_project_readme(project_dir: Path, project_name: str, mode: str, source: str | None) -> None:
    lines = [
        f"# {project_name}",
        "",
        "This is the software project workspace initialized by Echel.",
        "",
        "## Structure",
        "",
        "- `../echel-core/`: Echel framework, governance, and initialization artifacts",
        f"- `./`: Project codebase for `{project_name}`",
        "",
        "## Next steps",
        "",
        "1. Initialize this folder as its own Git repository.",
        "2. Start implementing software in this directory.",
        "3. Use `../echel-core` for governance and knowledge workflows.",
        "",
        f"Initialization mode: `{mode}`",
    ]
    if source:
        lines.append(f"Source path: `{source}`")
    lines.append("")
    (project_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


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
            f"- Generated split workspace with `echel-core/` and `{project_name}/`.\n"
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

    if workspace_dir.exists():
        raise SystemExit(f"Target workspace already exists: {workspace_dir}")

    echel_core_dir = workspace_dir / "echel-core"
    project_dir = workspace_dir / args.name

    workspace_dir.mkdir(parents=True, exist_ok=False)
    copy_core_template(repo_root, echel_core_dir)
    project_dir.mkdir(parents=True, exist_ok=False)
    write_workspace_gitignore(workspace_dir)
    write_project_readme(project_dir, args.name, args.mode, args.source)
    update_core_context(echel_core_dir, args.name, args.mode, args.source)

    print(f"Initialized workspace: {workspace_dir}")
    print(f"- Echel framework: {echel_core_dir}")
    print(f"- Project directory: {project_dir}")
    print("Next:")
    print(f"  cd {echel_core_dir} && make session-bootstrap")
    print(f"  cd {project_dir} && git init")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
