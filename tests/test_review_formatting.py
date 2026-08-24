import json
from pathlib import Path

from folderflow.formatting import (
    format_cleanup_review,
    format_cleanup_review_json,
)
from folderflow.review import CleanupCandidate, CleanupReview


def _review(tmp_path: Path) -> CleanupReview:
    keeper = tmp_path / "original.txt"
    candidate = CleanupCandidate(
        path=tmp_path / "copy.txt",
        size=20,
        category="Documents",
        reasons=("duplicate", "stale"),
        age_days=90,
        duplicate_of=keeper,
    )
    return CleanupReview(
        candidates=(candidate,),
        stale_bytes=20,
        duplicate_reclaimable_bytes=20,
    )


def test_formats_readable_cleanup_review(tmp_path: Path) -> None:
    output = format_cleanup_review(_review(tmp_path))

    assert "copy.txt [verified] 20 bytes: duplicate, stale" in output
    assert "keep" in output
    assert "90 days old" in output
    assert "Exact duplicate reclaimable bytes: 20" in output
    assert output.endswith("Review only: no files were changed.")


def test_formats_empty_cleanup_review() -> None:
    review = CleanupReview((), 0, 0)

    assert format_cleanup_review(review) == "No cleanup candidates found."


def test_formats_machine_readable_cleanup_review(
    tmp_path: Path,
) -> None:
    payload = json.loads(format_cleanup_review_json(_review(tmp_path)))

    assert payload["review_only"]
    assert payload["total_candidates"] == 1
    assert payload["total_candidate_bytes"] == 20
    assert payload["candidates"][0]["confidence"] == "verified"
