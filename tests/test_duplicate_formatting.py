import json
from pathlib import Path

from folderflow.duplicates import DuplicateGroup
from folderflow.formatting import format_duplicates, format_duplicates_json


def _group(tmp_path: Path) -> DuplicateGroup:
    return DuplicateGroup(
        digest="a" * 64,
        size=12,
        paths=(tmp_path / "one.txt", tmp_path / "two.txt"),
    )


def test_formats_readable_duplicate_report(tmp_path: Path) -> None:
    output = format_duplicates([_group(tmp_path)])

    assert "Group 1: 2 files, 12 bytes each" in output
    assert "one.txt" in output
    assert "Total: 1 groups, 12 reclaimable bytes" in output


def test_formats_empty_duplicate_report() -> None:
    assert format_duplicates([]) == "No exact duplicates found."


def test_formats_machine_readable_duplicate_report(tmp_path: Path) -> None:
    payload = json.loads(format_duplicates_json([_group(tmp_path)]))

    assert payload["total_groups"] == 1
    assert payload["reclaimable_bytes"] == 12
    assert payload["groups"][0]["digest"] == "a" * 64
    assert len(payload["groups"][0]["paths"]) == 2
