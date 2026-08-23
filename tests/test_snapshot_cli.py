from pathlib import Path

from folderflow.cli import build_parser, main
from folderflow.snapshots import snapshot_from_json


def test_snapshot_parser_requires_output() -> None:
    args = build_parser().parse_args([
        "snapshot",
        "downloads",
        "--recursive",
        "--output",
        "baseline.json",
        "--checksums",
    ])

    assert args.command == "snapshot"
    assert args.root == Path("downloads")
    assert args.recursive
    assert args.output == Path("baseline.json")
    assert args.checksums


def test_snapshot_command_captures_relative_paths(
    tmp_path: Path,
    capsys,
) -> None:
    folder = tmp_path / "downloads"
    folder.mkdir()
    (folder / "report.pdf").write_text("report")
    output = tmp_path / "baseline.json"

    result = main([
        "snapshot",
        str(folder),
        "--output",
        str(output),
    ])

    message = capsys.readouterr().out
    snapshot = snapshot_from_json(output.read_text())
    assert result == 0
    assert "with 1 files" in message
    assert snapshot.entries[0].path == "report.pdf"
    assert snapshot.entries[0].category == "Documents"


def test_snapshot_command_excludes_existing_output(
    tmp_path: Path,
    capsys,
) -> None:
    output = tmp_path / "baseline.json"
    output.write_text("{}")

    result = main([
        "snapshot",
        str(tmp_path),
        "--output",
        str(output),
        "--force",
    ])

    capsys.readouterr()
    snapshot = snapshot_from_json(output.read_text())
    assert result == 0
    assert snapshot.entries == ()


def test_snapshot_command_hashes_contents_when_requested(
    tmp_path: Path,
    capsys,
) -> None:
    folder = tmp_path / "downloads"
    folder.mkdir()
    (folder / "report.txt").write_text("hello")
    output = tmp_path / "verified.json"

    result = main([
        "snapshot",
        str(folder),
        "--output",
        str(output),
        "--checksums",
    ])

    capsys.readouterr()
    snapshot = snapshot_from_json(output.read_text())
    assert result == 0
    assert snapshot.has_checksums
    assert snapshot.entries[0].checksum == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e"
        "1b161e5c1fa7425e73043362938b9824"
    )
