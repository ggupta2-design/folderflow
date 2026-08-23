from pathlib import Path

from folderflow.snapshots import create_snapshot
from folderflow.verification import check_folder


def test_checks_live_folder_against_verified_baseline(
    tmp_path: Path,
) -> None:
    document = tmp_path / "document.txt"
    document.write_text("first")
    baseline = create_snapshot(
        [document],
        tmp_path,
        include_checksums=True,
    )
    document.write_text("later")

    diff = check_folder(baseline, [document], tmp_path)

    assert diff.checksums_compared
    assert diff.modified[0].reasons == (
        "modified_time",
        "content",
    )


def test_checks_added_and_removed_live_files(tmp_path: Path) -> None:
    removed = tmp_path / "removed.txt"
    removed.write_text("gone")
    baseline = create_snapshot([removed], tmp_path)
    removed.unlink()
    added = tmp_path / "added.txt"
    added.write_text("new")

    diff = check_folder(baseline, [added], tmp_path)

    assert [entry.path for entry in diff.added] == ["added.txt"]
    assert [entry.path for entry in diff.removed] == ["removed.txt"]
