import argparse
from pathlib import Path
from time import time

from .config import default_policy, load_policy
from .duplicates import find_duplicates
from .executor import apply_plan, rollback_plan
from .formatting import (
    format_duplicates,
    format_duplicates_json,
    format_inventory,
    format_inventory_json,
    format_plan,
    format_plan_json,
    format_snapshot_diff,
    format_snapshot_diff_json,
)
from .inventory import build_inventory, sort_inventory
from .manifest import read_manifest, write_manifest
from .planner import build_plan
from .reports import write_report
from .scanner import scan_files
from .snapshot_diff import compare_snapshots
from .snapshots import create_snapshot, snapshot_from_json, snapshot_to_json
from .verification import check_folder


def _scan_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--hidden", action="store_true", dest="include_hidden")
    parser.add_argument("--config", type=Path, help="JSON organization policy")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional relative-path pattern to ignore (repeatable)",
    )
    parser.add_argument("--min-size", type=int, dest="min_bytes")
    parser.add_argument("--max-size", type=int, dest="max_bytes")


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

    duplicates = commands.add_parser(
        "duplicates",
        help="Report exact duplicate files without deleting them",
    )
    _scan_options(duplicates)
    duplicates.add_argument("--json", action="store_true", dest="as_json")
    duplicates.add_argument("--output", type=Path, help="Save the report")
    duplicates.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing report",
    )
    duplicates.add_argument(
        "--minimum-copies",
        type=int,
        default=2,
        help="Only report groups with at least this many copies",
    )

    inventory = commands.add_parser(
        "inventory",
        help="Report storage usage without changing files",
    )
    _scan_options(inventory)
    inventory.add_argument(
        "--older-than-days",
        type=int,
        help="Only include files at least this old",
    )
    inventory.add_argument(
        "--sort",
        choices=("path", "largest", "oldest"),
        default="path",
    )
    inventory.add_argument("--json", action="store_true", dest="as_json")
    inventory.add_argument("--output", type=Path, help="Save the report")
    inventory.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing report",
    )

    check = commands.add_parser(
        "check",
        help="Compare a saved snapshot with its live folder",
    )
    check.add_argument("baseline", type=Path)
    _scan_options(check)
    check.add_argument("--json", action="store_true", dest="as_json")
    check.add_argument("--output", type=Path, help="Save the verification report")
    check.add_argument(
        "--fail-on-change",
        action="store_true",
        help="Return status 1 when changes are found",
    )
    check.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing verification report",
    )

    diff = commands.add_parser(
        "diff",
        help="Compare two saved folder snapshots",
    )
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    diff.add_argument("--json", action="store_true", dest="as_json")
    diff.add_argument("--output", type=Path, help="Save the change report")
    diff.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing change report",
    )

    snapshot = commands.add_parser(
        "snapshot",
        help="Capture portable folder metadata for later comparison",
    )
    _scan_options(snapshot)
    snapshot.add_argument("--output", type=Path, required=True)
    snapshot.add_argument(
        "--checksums",
        action="store_true",
        help="Hash file contents for verified comparisons",
    )
    snapshot.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing snapshot",
    )

    rollback = commands.add_parser("rollback", help="Undo moves from a manifest")
    rollback.add_argument("manifest", type=Path)
    rollback.add_argument("--yes", action="store_true", help="Confirm rollback")

    validate = commands.add_parser(
        "validate-policy",
        help="Validate a policy without scanning files",
    )
    validate.add_argument("policy", type=Path)
    return parser


def _scan(args: argparse.Namespace) -> tuple[Path, list, object]:
    root = args.root.expanduser().resolve()
    policy = load_policy(args.config) if args.config else default_policy()
    min_bytes = args.min_bytes if args.min_bytes is not None else policy.min_bytes
    max_bytes = args.max_bytes if args.max_bytes is not None else policy.max_bytes
    files = scan_files(
        root,
        recursive=args.recursive,
        include_hidden=args.include_hidden,
        exclude_patterns=(*policy.exclude_patterns, *args.exclude),
        min_bytes=min_bytes,
        max_bytes=max_bytes,
    )
    return root, files, policy


def _plan(args: argparse.Namespace) -> tuple[Path, list]:
    root, files, policy = _scan(args)
    return root, build_plan(files, root, categories=policy.categories)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "validate-policy":
        policy = load_policy(args.policy)
        print(
            f"Policy is valid: {len(policy.categories)} categories, "
            f"{len(policy.exclude_patterns)} exclusions."
        )
        return 0

    if args.command == "check":
        baseline_path = args.baseline.expanduser().resolve()
        baseline = snapshot_from_json(
            baseline_path.read_text(encoding="utf-8")
        )
        root, files, policy = _scan(args)
        excluded_outputs = {baseline_path}
        if args.output:
            excluded_outputs.add(args.output.expanduser().resolve())
        files = [
            path for path in files
            if path.resolve() not in excluded_outputs
        ]
        diff = check_folder(
            baseline,
            files,
            root,
            categories=policy.categories,
        )
        report = (
            format_snapshot_diff_json(diff)
            if args.as_json
            else format_snapshot_diff(diff)
        )
        if args.output:
            destination = write_report(
                report,
                args.output,
                overwrite=args.force,
            )
            print(f"Folder check written to {destination}")
        else:
            print(report)
        return 1 if args.fail_on_change and diff.has_changes else 0

    if args.command == "diff":
        before = snapshot_from_json(
            args.before.expanduser().read_text(encoding="utf-8")
        )
        after = snapshot_from_json(
            args.after.expanduser().read_text(encoding="utf-8")
        )
        diff = compare_snapshots(before, after)
        report = (
            format_snapshot_diff_json(diff)
            if args.as_json
            else format_snapshot_diff(diff)
        )
        if args.output:
            destination = write_report(
                report,
                args.output,
                overwrite=args.force,
            )
            print(f"Snapshot change report written to {destination}")
        else:
            print(report)
        return 0

    if args.command == "snapshot":
        root, files, policy = _scan(args)
        output_path = args.output.expanduser().resolve()
        files = [path for path in files if path.resolve() != output_path]
        snapshot = create_snapshot(
            files,
            root,
            categories=policy.categories,
            include_checksums=args.checksums,
        )
        destination = write_report(
            snapshot_to_json(snapshot),
            args.output,
            overwrite=args.force,
        )
        print(
            f"Snapshot written to {destination} "
            f"with {len(snapshot.entries)} files."
        )
        return 0

    if args.command == "inventory":
        _, files, policy = _scan(args)
        if args.output:
            output_path = args.output.expanduser().resolve()
            files = [path for path in files if path.resolve() != output_path]
        reference_time = time()
        records = build_inventory(
            files,
            categories=policy.categories,
            older_than_days=args.older_than_days,
            reference_time=reference_time,
        )
        records = sort_inventory(records, order=args.sort)
        report = (
            format_inventory_json(records, reference_time=reference_time)
            if args.as_json
            else format_inventory(records, reference_time=reference_time)
        )
        if args.output:
            destination = write_report(
                report,
                args.output,
                overwrite=args.force,
            )
            print(f"Inventory report written to {destination}")
        else:
            print(report)
        return 0

    if args.command == "duplicates":
        _, files, _ = _scan(args)
        if args.output:
            output_path = args.output.expanduser().resolve()
            files = [path for path in files if path.resolve() != output_path]
        groups = find_duplicates(files, minimum_copies=args.minimum_copies)
        report = (
            format_duplicates_json(groups)
            if args.as_json
            else format_duplicates(groups)
        )
        if args.output:
            destination = write_report(
                report,
                args.output,
                overwrite=args.force,
            )
            print(f"Duplicate report written to {destination}")
        else:
            print(report)
        return 0

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
