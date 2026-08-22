from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import time
from typing import Mapping

from .categories import DEFAULT_CATEGORIES, classify_file


SNAPSHOT_VERSION = 1


@dataclass(frozen=True)
class SnapshotEntry:
    path: str
    size: int
    modified_ns: int
    category: str

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "size": self.size,
            "modified_ns": self.modified_ns,
            "category": self.category,
        }


@dataclass(frozen=True)
class Snapshot:
    created_at: str
    entries: tuple[SnapshotEntry, ...]
    version: int = SNAPSHOT_VERSION

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "entries": [entry.to_dict() for entry in self.entries],
        }


def create_snapshot(
    files: list[Path],
    root: Path,
    *,
    categories: Mapping[str, frozenset[str]] = DEFAULT_CATEGORIES,
    created_at: float | None = None,
) -> Snapshot:
    root = root.expanduser().resolve()
    timestamp = time() if created_at is None else created_at
    entries: list[SnapshotEntry] = []
    for path in files:
        resolved = path.expanduser().resolve()
        relative = resolved.relative_to(root).as_posix()
        stat = resolved.stat()
        entries.append(SnapshotEntry(
            path=relative,
            size=stat.st_size,
            modified_ns=stat.st_mtime_ns,
            category=classify_file(resolved, categories),
        ))
    entries.sort(key=lambda entry: entry.path.casefold())
    return Snapshot(
        created_at=datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        ).isoformat(),
        entries=tuple(entries),
    )
