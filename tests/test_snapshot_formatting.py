import json

from folderflow.formatting import (
    format_snapshot_diff,
    format_snapshot_diff_json,
)
from folderflow.snapshot_diff import ModifiedEntry, SnapshotDiff
from folderflow.snapshots import SnapshotEntry


def _entry(
    path: str,
    size: int,
    checksum: str | None = None,
) -> SnapshotEntry:
    return SnapshotEntry(path, size, 100, "Documents", checksum)


def test_formats_readable_snapshot_changes() -> None:
    diff = SnapshotDiff(
        added=(_entry("new.txt", 5),),
        removed=(_entry("old.txt", 8),),
        modified=(
            ModifiedEntry(
                before=_entry("changed.txt", 10),
                after=_entry("changed.txt", 20),
                reasons=("size", "content"),
            ),
        ),
        unchanged=2,
        checksums_compared=True,
    )

    output = format_snapshot_diff(diff)

    assert "1 added, 1 removed, 1 modified, 2 unchanged" in output
    assert "Verification: SHA-256 contents compared" in output
    assert "+ new.txt" in output
    assert "- old.txt" in output
    assert "~ changed.txt: size, content (10 -> 20 bytes)" in output


def test_formats_unchanged_metadata_snapshot() -> None:
    diff = SnapshotDiff((), (), (), 3)

    assert format_snapshot_diff(diff) == (
        "No changes found. Unchanged: 3\n"
        "Verification: metadata only"
    )


def test_formats_json_snapshot_changes() -> None:
    diff = SnapshotDiff(
        (_entry("new.txt", 5, "a" * 64),),
        (),
        (),
        0,
        checksums_compared=True,
    )

    payload = json.loads(format_snapshot_diff_json(diff))

    assert payload["has_changes"]
    assert payload["checksums_compared"]
    assert payload["added"][0]["path"] == "new.txt"
    assert payload["added"][0]["checksum"] == "a" * 64
    assert payload["unchanged"] == 0
