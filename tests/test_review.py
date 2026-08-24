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
