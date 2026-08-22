import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
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


def snapshot_to_json(snapshot: Snapshot) -> str:
    return json.dumps(snapshot.to_dict(), indent=2)


def _require_non_negative_integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def snapshot_from_json(content: str) -> Snapshot:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid snapshot JSON: {error.msg}") from error
    if not isinstance(payload, dict):
        raise ValueError("Snapshot must be a JSON object")
    if payload.get("version") != SNAPSHOT_VERSION:
        raise ValueError(f"Unsupported snapshot version: {payload.get('version')}")
    created_at = payload.get("created_at")
    if not isinstance(created_at, str) or not created_at:
        raise ValueError("created_at must be a non-empty string")
    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list):
        raise ValueError("entries must be a list")

    entries: list[SnapshotEntry] = []
    seen_paths: set[str] = set()
    for index, raw in enumerate(raw_entries):
        if not isinstance(raw, dict):
            raise ValueError(f"entries[{index}] must be an object")
        path = raw.get("path")
        parsed_path = PurePosixPath(path) if isinstance(path, str) else None
        if (
            parsed_path is None
            or not path
            or parsed_path.is_absolute()
            or ".." in parsed_path.parts
        ):
            raise ValueError(f"entries[{index}].path must be a safe relative path")
        if path in seen_paths:
            raise ValueError(f"Duplicate snapshot path: {path}")
        seen_paths.add(path)
        category = raw.get("category")
        if not isinstance(category, str) or not category:
            raise ValueError(f"entries[{index}].category must be a non-empty string")
        entries.append(SnapshotEntry(
            path=path,
            size=_require_non_negative_integer(
                raw.get("size"),
                f"entries[{index}].size",
            ),
            modified_ns=_require_non_negative_integer(
                raw.get("modified_ns"),
                f"entries[{index}].modified_ns",
            ),
            category=category,
        ))

    entries.sort(key=lambda entry: entry.path.casefold())
    return Snapshot(
        version=SNAPSHOT_VERSION,
        created_at=created_at,
        entries=tuple(entries),
    )
