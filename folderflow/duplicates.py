import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DuplicateGroup:
    digest: str
    size: int
    paths: tuple[Path, ...]

    @property
    def reclaimable_bytes(self) -> int:
        return self.size * (len(self.paths) - 1)

    def to_dict(self) -> dict:
        return {
            "digest": self.digest,
            "size": self.size,
            "reclaimable_bytes": self.reclaimable_bytes,
            "paths": [str(path) for path in self.paths],
        }


def _sha256(path: Path, *, chunk_size: int) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(
    files: list[Path],
    *,
    chunk_size: int = 1024 * 1024,
    minimum_copies: int = 2,
) -> list[DuplicateGroup]:
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    if minimum_copies < 2:
        raise ValueError("minimum_copies must be at least 2")

    by_size: dict[int, list[Path]] = {}
    seen_files: set[tuple[int, int]] = set()
    for path in files:
        stat = path.stat()
        identity = (stat.st_dev, stat.st_ino)
        if identity in seen_files:
            continue
        seen_files.add(identity)
        by_size.setdefault(stat.st_size, []).append(path)

    groups: list[DuplicateGroup] = []
    for size, candidates in by_size.items():
        if len(candidates) < minimum_copies:
            continue
        by_digest: dict[str, list[Path]] = {}
        for path in candidates:
            digest = _sha256(path, chunk_size=chunk_size)
            by_digest.setdefault(digest, []).append(path)
        for digest, matches in by_digest.items():
            if len(matches) >= minimum_copies:
                groups.append(DuplicateGroup(
                    digest=digest,
                    size=size,
                    paths=tuple(sorted(matches)),
                ))

    return sorted(groups, key=lambda group: (-group.reclaimable_bytes, group.digest))
