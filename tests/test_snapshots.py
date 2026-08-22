from pathlib import Path

import pytest

from folderflow.snapshots import SNAPSHOT_VERSION, create_snapshot


def test_snapshot_uses_relative_sorted_paths(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    second = nested / "B.txt"
    first = tmp_path / "a.pdf"
    second.write_text("two")
    first.write_text("one")

    snapshot = create_snapshot(
        [second, first],
        tmp_path,
        created_at=2_000_000_000.0,
    )

    assert snapshot.version == SNAPSHOT_VERSION
    assert snapshot.created_at == "2033-05-18T03:33:20+00:00"
    assert [entry.path for entry in snapshot.entries] == [
        "a.pdf",
        "nested/B.txt",
    ]
    assert snapshot.entries[0].category == "Documents"
    assert snapshot.entries[0].size == 3


def test_snapshot_uses_custom_categories(tmp_path: Path) -> None:
    notebook = tmp_path / "analysis.ipynb"
    notebook.write_text("{}")

    snapshot = create_snapshot(
        [notebook],
        tmp_path,
        categories={"Notebooks": frozenset({".ipynb"})},
    )

    assert snapshot.entries[0].category == "Notebooks"


def test_snapshot_rejects_files_outside_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside")

    with pytest.raises(ValueError):
        create_snapshot([outside], root)
