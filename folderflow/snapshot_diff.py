from dataclasses import dataclass

from .snapshots import Snapshot, SnapshotEntry


@dataclass(frozen=True)
class ModifiedEntry:
    before: SnapshotEntry
    after: SnapshotEntry

    def to_dict(self) -> dict:
        return {
            "path": self.after.path,
            "before": self.before.to_dict(),
            "after": self.after.to_dict(),
        }


@dataclass(frozen=True)
class SnapshotDiff:
    added: tuple[SnapshotEntry, ...]
    removed: tuple[SnapshotEntry, ...]
    modified: tuple[ModifiedEntry, ...]
    unchanged: int

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def to_dict(self) -> dict:
        return {
            "added": [entry.to_dict() for entry in self.added],
            "removed": [entry.to_dict() for entry in self.removed],
            "modified": [change.to_dict() for change in self.modified],
            "unchanged": self.unchanged,
        }


def compare_snapshots(before: Snapshot, after: Snapshot) -> SnapshotDiff:
    before_by_path = {entry.path: entry for entry in before.entries}
    after_by_path = {entry.path: entry for entry in after.entries}
    before_paths = set(before_by_path)
    after_paths = set(after_by_path)

    added = tuple(
        after_by_path[path]
        for path in sorted(after_paths - before_paths, key=str.casefold)
    )
    removed = tuple(
        before_by_path[path]
        for path in sorted(before_paths - after_paths, key=str.casefold)
    )
    modified: list[ModifiedEntry] = []
    unchanged = 0
    for path in sorted(before_paths & after_paths, key=str.casefold):
        old = before_by_path[path]
        new = after_by_path[path]
        if old == new:
            unchanged += 1
        else:
            modified.append(ModifiedEntry(before=old, after=new))

    return SnapshotDiff(
        added=added,
        removed=removed,
        modified=tuple(modified),
        unchanged=unchanged,
    )
