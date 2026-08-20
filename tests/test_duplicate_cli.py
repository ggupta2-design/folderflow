import json
from pathlib import Path

from folderflow.cli import build_parser, main


def test_duplicates_parser_supports_recursive_json() -> None:
    args = build_parser().parse_args([
        "duplicates",
        "downloads",
        "--recursive",
        "--json",
    ])

    assert args.command == "duplicates"
    assert args.root == Path("downloads")
    assert args.recursive
    assert args.as_json


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
