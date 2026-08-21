import json
from pathlib import Path

from folderflow.formatting import format_inventory, format_inventory_json
from folderflow.inventory import FileRecord


REFERENCE = 2_000_000_000.0


def _records(tmp_path: Path) -> list[FileRecord]:
    return [
        FileRecord(
            tmp_path / "report.pdf",
            20,
            REFERENCE - 10 * 86400,
            "Documents",
        ),
        FileRecord(
            tmp_path / "photo.jpg",
            30,
            REFERENCE - 5 * 86400,
            "Images",
        ),
    ]


def test_formats_readable_inventory(tmp_path: Path) -> None:
    output = format_inventory(_records(tmp_path), reference_time=REFERENCE)

    assert "report.pdf [Documents] 20 bytes, 10 days old" in output
    assert "Total: 2 files, 50 bytes" in output
    assert "Images: 1 files, 30 bytes" in output


def test_formats_empty_inventory() -> None:
    assert format_inventory([], reference_time=REFERENCE) == (
        "No files matched the inventory filters."
    )


def test_formats_json_inventory(tmp_path: Path) -> None:
    payload = json.loads(
        format_inventory_json(_records(tmp_path), reference_time=REFERENCE)
    )

    assert payload["total_files"] == 2
    assert payload["total_bytes"] == 50
    assert payload["by_category"]["Documents"]["bytes"] == 20
    assert payload["files"][0]["age_days"] == 10
    assert payload["files"][0]["modified_at"].endswith("+00:00")
