import json
from pathlib import Path

from folderflow.cli import build_parser, main
from folderflow.snapshots import (
    create_snapshot,
    snapshot_to_json,
)


def _baseline(folder: Path, destination: Path) -> None:
    files = sorted(folder.iterdir())
    snapshot = create_snapshot(
        files,
        folder,
        include_checksums=True,
    )
    destination.write_text(snapshot_to_json(snapshot))


def test_check_parser_accepts_baseline_and_folder() -> None:
    args = build_parser().parse_args([
        "check",
        "baseline.json",
        "documents",
        "--recursive",
        "--json",
    ])

    assert args.command == "check"
    assert args.baseline == Path("baseline.json")
    assert args.root == Path("documents")
    assert args.recursive
    assert args.as_json


def test_check_command_detects_live_content_changes(
    tmp_path: Path,
    capsys,
) -> None:
    folder = tmp_path / "documents"
    folder.mkdir()
    document = folder / "report.txt"
    document.write_text("first")
    baseline = tmp_path / "baseline.json"
    _baseline(folder, baseline)
    document.write_text("changed")

    result = main([
        "check",
        str(baseline),
        str(folder),
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["checksums_compared"]
    assert payload["modified"][0]["path"] == "report.txt"
    assert "content" in payload["modified"][0]["reasons"]


def test_check_command_exports_unchanged_report(
    tmp_path: Path,
    capsys,
) -> None:
    folder = tmp_path / "documents"
    folder.mkdir()
    (folder / "report.txt").write_text("same")
    baseline = tmp_path / "baseline.json"
    output = tmp_path / "check.json"
    _baseline(folder, baseline)

    result = main([
        "check",
        str(baseline),
        str(folder),
        "--json",
        "--output",
        str(output),
    ])

    message = capsys.readouterr().out
    payload = json.loads(output.read_text())
    assert result == 0
    assert "Folder check written to" in message
    assert not payload["has_changes"]
    assert payload["unchanged"] == 1


def test_check_can_fail_when_automation_detects_changes(
    tmp_path: Path,
    capsys,
) -> None:
    folder = tmp_path / "documents"
    folder.mkdir()
    document = folder / "report.txt"
    document.write_text("before")
    baseline = tmp_path / "baseline.json"
    _baseline(folder, baseline)
    document.write_text("after")

    result = main([
        "check",
        str(baseline),
        str(folder),
        "--fail-on-change",
    ])

    capsys.readouterr()
    assert result == 1


def test_fail_on_change_succeeds_for_unchanged_folder(
    tmp_path: Path,
    capsys,
) -> None:
    folder = tmp_path / "documents"
    folder.mkdir()
    (folder / "report.txt").write_text("same")
    baseline = tmp_path / "baseline.json"
    _baseline(folder, baseline)

    result = main([
        "check",
        str(baseline),
        str(folder),
        "--fail-on-change",
    ])

    capsys.readouterr()
    assert result == 0
