import json
from pathlib import Path

from folderflow.cli import build_parser, main
from folderflow.snapshots import Snapshot, SnapshotEntry, snapshot_to_json


def _entry(path: str, size: int = 10) -> SnapshotEntry:
    return SnapshotEntry(path, size, 100, "Documents")


def _write(path: Path, snapshot: Snapshot) -> None:
    path.write_text(snapshot_to_json(snapshot))


def test_diff_parser_accepts_two_snapshots() -> None:
    args = build_parser().parse_args([
        "diff",
        "before.json",
        "after.json",
        "--json",
    ])

    assert args.command == "diff"
    assert args.before == Path("before.json")
    assert args.after == Path("after.json")
    assert args.as_json


def test_diff_command_reports_folder_changes(
    tmp_path: Path,
    capsys,
) -> None:
    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    _write(before_path, Snapshot("before", (_entry("old.txt"),)))
    _write(after_path, Snapshot("after", (_entry("new.txt"),)))

    result = main([
        "diff",
        str(before_path),
        str(after_path),
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["has_changes"]
    assert payload["added"][0]["path"] == "new.txt"
    assert payload["removed"][0]["path"] == "old.txt"


def test_diff_command_exports_change_report(
    tmp_path: Path,
    capsys,
) -> None:
    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    report = tmp_path / "changes.txt"
    snapshot = Snapshot("now", (_entry("same.txt"),))
    _write(before_path, snapshot)
    _write(after_path, snapshot)

    result = main([
        "diff",
        str(before_path),
        str(after_path),
        "--output",
        str(report),
    ])

    message = capsys.readouterr().out
    assert result == 0
    assert "Snapshot change report written to" in message
    assert report.read_text() == (\n        "No changes found. Unchanged: 1\\n"\n        "Verification: metadata only\\n"\n    )
