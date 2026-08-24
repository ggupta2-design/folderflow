import os
from pathlib import Path

import pytest

from folderflow.review import build_cleanup_review


REFERENCE = 2_000_000_000.0


def _file(
    path: Path,
    content: str,
    *,
    age_days: int = 0,
) -> Path:
    path.write_text(content)
    modified = REFERENCE - age_days * 86400
    os.utime(path, (modified, modified))
    return path


def test_builds_stale_file_candidates(tmp_path: Path) -> None:
    old = _file(tmp_path / "old.pdf", "old", age_days=90)
    recent = _file(tmp_path / "recent.pdf", "new", age_days=10)

    review = build_cleanup_review(
        [old, recent],
        older_than_days=60,
        include_duplicates=False,
        reference_time=REFERENCE,
    )

    assert len(review.candidates) == 1
    candidate = review.candidates[0]
    assert candidate.path == old
    assert candidate.reasons == ("stale",)
    assert candidate.age_days == 90
    assert candidate.category == "Documents"
    assert candidate.confidence == "review"
    assert review.stale_bytes == 3


def test_stale_boundary_is_inclusive(tmp_path: Path) -> None:
    boundary = _file(tmp_path / "boundary.txt", "x", age_days=30)

    review = build_cleanup_review(
        [boundary],
        older_than_days=30,
        include_duplicates=False,
        reference_time=REFERENCE,
    )

    assert review.candidates[0].path == boundary


def test_requires_at_least_one_review_signal() -> None:
    with pytest.raises(ValueError, match="Enable duplicate review"):
        build_cleanup_review([], include_duplicates=False)


def test_recommends_deterministic_duplicate_copies(
    tmp_path: Path,
) -> None:
    first = _file(tmp_path / "a.txt", "same")
    second = _file(tmp_path / "b.txt", "same")
    unique = _file(tmp_path / "unique.txt", "different")

    review = build_cleanup_review(
        [second, unique, first],
        reference_time=REFERENCE,
    )

    assert len(review.candidates) == 1
    candidate = review.candidates[0]
    assert candidate.path == second
    assert candidate.duplicate_of == first
    assert candidate.reasons == ("duplicate",)
    assert candidate.confidence == "verified"
    assert review.duplicate_reclaimable_bytes == 4


def test_does_not_recommend_unique_files(tmp_path: Path) -> None:
    unique = _file(tmp_path / "unique.txt", "only")

    review = build_cleanup_review(
        [unique],
        reference_time=REFERENCE,
    )

    assert review.candidates == ()
    assert review.duplicate_reclaimable_bytes == 0
