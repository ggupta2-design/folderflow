import json
from pathlib import Path

from folderflow.cli import build_parser
from folderflow.formatting import format_plan, format_plan_json
from folderflow.planner import Move


def test_plan_parser_supports_recursive_json_preview() -> None:
    args = build_parser().parse_args([
        "plan",
        "downloads",
        "--recursive",
        "--json",
    ])

    assert args.command == "plan"
    assert args.root == Path("downloads")
    assert args.recursive
    assert args.as_json


def test_apply_requires_explicit_confirmation_flag() -> None:
    args = build_parser().parse_args(["apply", "downloads"])

    assert not args.yes


def test_rollback_parser_accepts_manifest() -> None:
    args = build_parser().parse_args(["rollback", "run.json", "--yes"])

    assert args.manifest == Path("run.json")
    assert args.yes


def test_text_preview_includes_moves_and_summary(tmp_path: Path) -> None:
    move = Move(
        tmp_path / "report.pdf",
        tmp_path / "Documents" / "report.pdf",
        "Documents",
    )

    output = format_plan([move])

    assert "report.pdf" in output
    assert "Documents: 1" in output
    assert "Total: 1" in output


def test_json_preview_is_machine_readable(tmp_path: Path) -> None:
    move = Move(
        tmp_path / "photo.jpg",
        tmp_path / "Images" / "photo.jpg",
        "Images",
    )

    payload = json.loads(format_plan_json([move]))

    assert payload["total"] == 1
    assert payload["summary"] == {"Images": 1}
    assert payload["moves"][0]["category"] == "Images"
