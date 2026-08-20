import json
from pathlib import Path

from folderflow.cli import build_parser, main


def test_duplicates_parser_supports_recursive_json() -> None:
    args = build_parser().parse_args([
        "duplicates",
        "downloads",
        "--recursive",
        "--json",
        "--minimum-copies",
        "3",
    ])

    assert args.command == "duplicates"
    assert args.root == Path("downloads")
    assert args.recursive
    assert args.as_json
    assert args.minimum_copies == 3


def test_duplicates_command_reports_matches(
    tmp_path: Path,
    capsys,
) -> None:
    (tmp_path / "original.txt").write_text("same content")
    (tmp_path / "copy.txt").write_text("same content")
    (tmp_path / "unique.txt").write_text("different")

    result = main(["duplicates", str(tmp_path), "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["total_groups"] == 1
    assert payload["groups"][0]["size"] == 12
    assert payload["reclaimable_bytes"] == 12


def test_duplicates_command_honors_exclusions(
    tmp_path: Path,
    capsys,
) -> None:
    (tmp_path / "one.log").write_text("same")
    (tmp_path / "two.log").write_text("same")

    result = main([
        "duplicates",
        str(tmp_path),
        "--exclude",
        "*.log",
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["total_groups"] == 0


def test_duplicates_command_applies_copy_threshold(
    tmp_path: Path,
    capsys,
) -> None:
    (tmp_path / "one.txt").write_text("same")
    (tmp_path / "two.txt").write_text("same")

    result = main([
        "duplicates",
        str(tmp_path),
        "--minimum-copies",
        "3",
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["total_groups"] == 0


def test_duplicates_command_exports_json_report(
    tmp_path: Path,
    capsys,
) -> None:
    (tmp_path / "one.txt").write_text("same")
    (tmp_path / "two.txt").write_text("same")
    report = tmp_path / "report.json"

    result = main([
        "duplicates",
        str(tmp_path),
        "--json",
        "--output",
        str(report),
    ])

    message = capsys.readouterr().out
    payload = json.loads(report.read_text())
    assert result == 0
    assert "Duplicate report written to" in message
    assert payload["total_groups"] == 1


def test_duplicate_export_requires_force_to_replace(
    tmp_path: Path,
) -> None:
    report = tmp_path / "report.txt"
    report.write_text("old")

    result = main([
        "duplicates",
        str(tmp_path),
        "--output",
        str(report),
        "--force",
    ])

    assert result == 0
    assert report.read_text() == "No exact duplicates found.\n"
