from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import Mapping

from .categories import DEFAULT_CATEGORIES, classify_file
from .duplicates import find_duplicates
from .inventory import build_inventory


@dataclass(frozen=True)
class CleanupCandidate:
    path: Path
    size: int
    category: str
    reasons: tuple[str, ...]
    age_days: int | None = None
    duplicate_of: Path | None = None

    @property
    def confidence(self) -> str:
        return "verified" if "duplicate" in self.reasons else "review"

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "size": self.size,
            "category": self.category,
            "reasons": list(self.reasons),
            "confidence": self.confidence,
            "age_days": self.age_days,
            "duplicate_of": (
                str(self.duplicate_of)
                if self.duplicate_of is not None
                else None
            ),
        }


@dataclass(frozen=True)
class CleanupReview:
    candidates: tuple[CleanupCandidate, ...]
    stale_bytes: int
    duplicate_reclaimable_bytes: int

    @property
    def total_candidate_bytes(self) -> int:
        return sum(candidate.size for candidate in self.candidates)

    def to_dict(self) -> dict:
        return {
            "total_candidates": len(self.candidates),
            "total_candidate_bytes": self.total_candidate_bytes,
            "stale_bytes": self.stale_bytes,
            "duplicate_reclaimable_bytes": self.duplicate_reclaimable_bytes,
            "candidates": [
                candidate.to_dict() for candidate in self.candidates
            ],
        }


def build_cleanup_review(
    files: list[Path],
    *,
    categories: Mapping[str, frozenset[str]] = DEFAULT_CATEGORIES,
    older_than_days: int | None = None,
    include_duplicates: bool = True,
    minimum_copies: int = 2,
    reference_time: float | None = None,
) -> CleanupReview:
    if older_than_days is None and not include_duplicates:
        raise ValueError(
            "Enable duplicate review or provide older_than_days"
        )
    reference = time() if reference_time is None else reference_time
    by_path: dict[Path, dict] = {}
    stale_bytes = 0

    if older_than_days is not None:
        stale = build_inventory(
            files,
            categories=categories,
            older_than_days=older_than_days,
            reference_time=reference,
        )
        for record in stale:
            age_days = record.age_days(reference_time=reference)
            by_path[record.path] = {
                "size": record.size,
                "category": record.category,
                "reasons": {"stale"},
                "age_days": age_days,
                "duplicate_of": None,
            }
            stale_bytes += record.size

    duplicate_reclaimable = 0
    if include_duplicates:
        for group in find_duplicates(
            files,
            minimum_copies=minimum_copies,
        ):
            keeper, *copies = group.paths
            duplicate_reclaimable += group.reclaimable_bytes
            for copy in copies:
                details = by_path.setdefault(copy, {
                    "size": group.size,
                    "category": classify_file(copy, categories),
                    "reasons": set(),
                    "age_days": None,
                    "duplicate_of": None,
                })
                details["reasons"].add("duplicate")
                details["duplicate_of"] = keeper

    candidates = tuple(
        CleanupCandidate(
            path=path,
            size=details["size"],
            category=details["category"],
            reasons=tuple(sorted(details["reasons"])),
            age_days=details["age_days"],
            duplicate_of=details["duplicate_of"],
        )
        for path, details in sorted(
            by_path.items(),
            key=lambda item: (-item[1]["size"], str(item[0]).casefold()),
        )
    )
    return CleanupReview(
        candidates=candidates,
        stale_bytes=stale_bytes,
        duplicate_reclaimable_bytes=duplicate_reclaimable,
    )
