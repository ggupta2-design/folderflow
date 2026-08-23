from folderflow.snapshot_diff import compare_snapshots
from folderflow.snapshots import Snapshot, SnapshotEntry


def _entry(
    path: str,
    *,
    size: int = 10,
    modified_ns: int = 100,
    category: str = "Documents",
    checksum: str | None = None,
) -> SnapshotEntry:
    return SnapshotEntry(path, size, modified_ns, category, checksum)


def test_compares_added_removed_modified_and_unchanged_files() -> None:
    before = Snapshot(
        "before",
        (
            _entry("removed.txt"),
            _entry("changed.txt", size=10),
            _entry("same.txt"),
        ),
    )
    after = Snapshot(
        "after",
        (
            _entry("added.txt"),
            _entry("changed.txt", size=20, modified_ns=200),
            _entry("same.txt"),
        ),
    )

    diff = compare_snapshots(before, after)

    assert [entry.path for entry in diff.added] == ["added.txt"]
    assert [entry.path for entry in diff.removed] == ["removed.txt"]
    assert [change.after.path for change in diff.modified] == ["changed.txt"]
    assert diff.modified[0].reasons == ("size", "modified_time")
    assert diff.modified[0].before.size == 10
    assert diff.modified[0].after.size == 20
    assert diff.unchanged == 1
    assert diff.has_changes


def test_identical_snapshots_have_no_changes() -> None:
    snapshot = Snapshot("now", (_entry("same.txt"),))

    diff = compare_snapshots(snapshot, snapshot)

    assert not diff.has_changes
    assert diff.unchanged == 1
    assert diff.to_dict() == {
        "added": [],
        "removed": [],
        "modified": [],
        "unchanged": 1,
        "checksums_compared": False,
    }


def test_category_change_is_reported() -> None:
    before = Snapshot("before", (_entry("data.csv"),))
    after = Snapshot(
        "after",
        (_entry("data.csv", category="Spreadsheets"),),
    )

    diff = compare_snapshots(before, after)

    assert diff.modified[0].reasons == ("category",)


def test_checksum_detects_same_size_content_change() -> None:
    before = Snapshot(
        "before",
        (_entry("data.bin", checksum="a" * 64),),
    )
    after = Snapshot(
        "after",
        (_entry("data.bin", checksum="b" * 64),),
    )

    diff = compare_snapshots(before, after)

    assert diff.checksums_compared
    assert diff.modified[0].reasons == ("content",)


def test_missing_checksum_does_not_create_false_change() -> None:
    before = Snapshot("before", (_entry("same.txt"),))
    after = Snapshot(
        "after",
        (_entry("same.txt", checksum="a" * 64),),
    )

    diff = compare_snapshots(before, after)

    assert not diff.has_changes
    assert not diff.checksums_compared
