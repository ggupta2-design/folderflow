from pathlib import Path

from folderflow.analytics import summarize_inventory
from folderflow.inventory import FileRecord


def test_summarizes_inventory_by_category(tmp_path: Path) -> None:
    records = [
        FileRecord(tmp_path / "one.pdf", 10, 1000.0, "Documents"),
        FileRecord(tmp_path / "two.pdf", 15, 1100.0, "Documents"),
        FileRecord(tmp_path / "photo.jpg", 30, 1200.0, "Images"),
    ]

    summary = summarize_inventory(records)

    assert summary.total_files == 3
    assert summary.total_bytes == 55
    assert summary.by_category["Documents"].files == 2
    assert summary.by_category["Documents"].bytes == 25
    assert summary.by_category["Images"].to_dict() == {
        "files": 1,
        "bytes": 30,
    }


def test_empty_inventory_has_zero_totals() -> None:
    summary = summarize_inventory([])

    assert summary.to_dict() == {
        "total_files": 0,
        "total_bytes": 0,
        "by_category": {},
    }
