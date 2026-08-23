from pathlib import Path
from typing import Mapping

from .categories import DEFAULT_CATEGORIES
from .snapshot_diff import SnapshotDiff, compare_snapshots
from .snapshots import Snapshot, create_snapshot


def check_folder(
    baseline: Snapshot,
    files: list[Path],
    root: Path,
    *,
    categories: Mapping[str, frozenset[str]] = DEFAULT_CATEGORIES,
) -> SnapshotDiff:
    current = create_snapshot(
        files,
        root,
        categories=categories,
        include_checksums=baseline.has_checksums,
    )
    return compare_snapshots(baseline, current)
