import os
from pathlib import Path

import pytest

from folderflow.inventory import FileRecord, build_inventory, sort_inventory


REFERENCE = 2_000_000_000.0


def _file(path: Path, content: str, modified_at: float) -> Path:
    path.write_text(content)
    os.utime(path, (modified_at, modified_at))
    return path


def test_inventory_records_file_metadata(tmp_path: Path) -> None:
    document = _file(
        tmp_path / "report.pdf",
        "report",
        REFERENCE - 3 * 86400,
    )

    records = build_inventory([document], reference_time=REFERENCE)

    assert len(records) == 1
    assert records[0].path == document
    assert records[0].size == 6
    assert records[0].category == "Documents"
    assert records[0].age_days(reference_time=REFERENCE) == 3
    assert records[0].to_dict(reference_time=REFERENCE)["age_days"] == 3


def test_inventory_filters_by_inclusive_age(tmp_path: Path) -> None:
    old = _file(tmp_path / "old.txt", "old", REFERENCE - 30 * 86400)
    recent = _file(tmp_path / "recent.txt", "new", REFERENCE - 29 * 86400)

    records = build_inventory(
        [old, recent],
        older_than_days=30,
        reference_time=REFERENCE,
    )

    assert [record.path for record in records] == [old]


def test_inventory_uses_custom_categories(tmp_path: Path) -> None:
    notebook = _file(tmp_path / "work.ipynb", "{}", REFERENCE)

    records = build_inventory(
        [notebook],
        categories={"Notebooks": frozenset({".ipynb"})},
        reference_time=REFERENCE,
    )

    assert records[0].category == "Notebooks"


def test_inventory_rejects_negative_age() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        build_inventory([], older_than_days=-1)


def test_sorts_inventory_for_different_review_tasks(tmp_path: Path) -> None:
    small_old = FileRecord(tmp_path / "z.txt", 10, 100.0, "Documents")
    large_new = FileRecord(tmp_path / "a.txt", 100, 200.0, "Documents")
    records = [small_old, large_new]

    assert sort_inventory(records, order="path") == [large_new, small_old]
    assert sort_inventory(records, order="largest") == [large_new, small_old]
    assert sort_inventory(records, order="oldest") == [small_old, large_new]


def test_rejects_unknown_inventory_order() -> None:
    with pytest.raises(ValueError, match="Unknown inventory order"):
        sort_inventory([], order="random")
