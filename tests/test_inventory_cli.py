import json
import os
from pathlib import Path
from time import time

from folderflow.cli import build_parser, main


def test_inventory_parser_accepts_review_options() -> None:
    args = build_parser().parse_args([
        "inventory",
        "downloads",
        "--recursive",
        "--older-than-days",
        "30",
        "--sort",
        "largest",
        "--json",
    ])

    assert args.command == "inventory"
    assert args.root == Path("downloads")
    assert args.recursive
    assert args.older_than_days == 30
    assert args.sort == "largest"
    assert args.as_json


def test_inventory_command_filters_and_summarizes_storage(
    tmp_path: Path,
    capsys,
) -> None:
    old = tmp_path / "archive.pdf"
    recent = tmp_path / "recent.jpg"
    old.write_bytes(b"old document")
    recent.write_bytes(b"new image")
    old_time = time() - 45 * 86400
    os.utime(old, (old_time, old_time))

    result = main([
        "inventory",
        str(tmp_path),
        "--older-than-days",
        "30",
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["total_files"] == 1
    assert payload["total_bytes"] == 12
    assert payload["by_category"]["Documents"]["files"] == 1
    assert payload["files"][0]["path"].endswith("archive.pdf")


def test_inventory_command_sorts_largest_first(
    tmp_path: Path,
    capsys,
) -> None:
    (tmp_path / "small.txt").write_text("a")
    (tmp_path / "large.txt").write_text("abcdefghij")

    result = main([
        "inventory",
        str(tmp_path),
        "--sort",
        "largest",
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["files"][0]["path"].endswith("large.txt")
