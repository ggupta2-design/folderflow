import argparse
from pathlib import Path

from .executor import apply_plan, rollback_plan
from .formatting import format_plan, format_plan_json
from .manifest import read_manifest, write_manifest
from .planner import build_plan
from .scanner import scan_files


def _scan_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--hidden", action="store_true", dest="include_hidden")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="folderflow")
    commands = parser.add_subparsers(dest="command", required=True)

    preview = commands.add_parser("plan", help="Preview file organization")
    _scan_options(preview)
    preview.add_argument("--json", action="store_true", dest="as_json")

    apply = commands.add_parser("apply", help="Apply a reviewed organization plan")
    _scan_options(apply)
    apply.add_argument("--manifest", type=Path)
    apply.add_argument("--yes", action="store_true", help="Confirm file moves")

    rollback = commands.add_parser("rollback", help="Undo moves from a manifest")
    rollback.add_argument("manifest", type=Path)
    rollback.add_argument("--yes", action="store_true", help="Confirm rollback")
    return parser


def _plan(args: argparse.Namespace) -> tuple[Path, list]:
    root = args.root.expanduser().resolve()
    files = scan_files(
        root,
        recursive=args.recursive,
        include_hidden=args.include_hidden,
    )
    return root, build_plan(files, root)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "plan":
        _, plan = _plan(args)
        print(format_plan_json(plan) if args.as_json else format_plan(plan))
        return 0

    if args.command == "apply":
        root, plan = _plan(args)
        print(format_plan(plan))
        if not args.yes:
            print("No files moved. Run again with --yes after reviewing the plan.")
            return 2
        manifest = args.manifest or root / ".folderflow-last-run.json"
        write_manifest(plan, manifest, root=root)
        moved = apply_plan(plan)
        print(f"Moved {moved} files. Undo manifest: {manifest}")
        return 0

    plan = read_manifest(args.manifest)
    if not args.yes:
        print(f"No files restored. Add --yes to roll back {len(plan)} moves.")
        return 2
    restored = rollback_plan(plan)
    print(f"Restored {restored} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
