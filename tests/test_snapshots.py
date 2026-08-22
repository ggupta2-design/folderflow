from pathlib import Path

import pytest

from folderflow.snapshots import (
    SNAPSHOT_VERSION,
    create_snapshot,
    snapshot_from_json,
    snapshot_to_json,
)


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


def test_snapshot_json_round_trip(tmp_path: Path) -> None:
    document = tmp_path / "report.pdf"
    document.write_text("report")
    snapshot = create_snapshot([document], tmp_path, created_at=1000.0)

    restored = snapshot_from_json(snapshot_to_json(snapshot))

    assert restored == snapshot


@pytest.mark.parametrize(
    "content, message",
    [
        ('{"version": 99, "created_at": "now", "entries": []}', "version"),
        ('{"version": 1, "created_at": "now", "entries": {}}', "list"),
        (
            '{"version": 1, "created_at": "now", "entries": '
            '[{"path": "../secret", "size": 1, "modified_ns": 1, '
            '"category": "Other"}]}',
            "safe relative path",
        ),
        (
            '{"version": 1, "created_at": "now", "entries": '
            '[{"path": "a", "size": -1, "modified_ns": 1, '
            '"category": "Other"}]}',
            "non-negative",
        ),
    ],
)
def test_rejects_invalid_snapshot_payloads(
    content: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        snapshot_from_json(content)
