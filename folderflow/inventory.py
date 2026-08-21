from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import time
from typing import Mapping

from .categories import DEFAULT_CATEGORIES, classify_file


@dataclass(frozen=True)
class FileRecord:
    path: Path
    size: int
    modified_at: float
    category: str

    def age_days(self, *, reference_time: float) -> int:
        return max(0, int((reference_time - self.modified_at) // 86400))

    def to_dict(self, *, reference_time: float) -> dict:
        modified = datetime.fromtimestamp(
            self.modified_at,
            tz=timezone.utc,
        ).isoformat()
        return {
            "path": str(self.path),
            "size": self.size,
            "modified_at": modified,
            "age_days": self.age_days(reference_time=reference_time),
            "category": self.category,
        }


def build_inventory(
    files: list[Path],
    *,
    categories: Mapping[str, frozenset[str]] = DEFAULT_CATEGORIES,
    older_than_days: int | None = None,
    reference_time: float | None = None,
) -> list[FileRecord]:
    if older_than_days is not None and older_than_days < 0:
        raise ValueError("older_than_days must be non-negative")

    reference = time() if reference_time is None else reference_time
    cutoff = (
        reference - older_than_days * 86400
        if older_than_days is not None
        else None
    )
    records: list[FileRecord] = []
    for path in files:
        stat = path.stat()
        if cutoff is not None and stat.st_mtime > cutoff:
            continue
        records.append(FileRecord(
            path=path,
            size=stat.st_size,
            modified_at=stat.st_mtime,
            category=classify_file(path, categories),
        ))
    return records
