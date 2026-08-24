import json

from .analytics import summarize_inventory
from .duplicates import DuplicateGroup
from .inventory import FileRecord
from .planner import Move, summarize_plan
from .review import CleanupReview
from .snapshot_diff import SnapshotDiff


def format_plan(plan: list[Move]) -> str:
    if not plan:
        return "No files need organizing."
    lines = [
        f"{move.source} -> {move.destination} [{move.category}]"
        for move in plan
    ]
    summary = ", ".join(
        f"{category}: {count}"
        for category, count in summarize_plan(plan).items()
    )
    return "\n".join([*lines, f"Total: {len(plan)} ({summary})"])


def format_plan_json(plan: list[Move]) -> str:
    return json.dumps(
        {
            "total": len(plan),
            "summary": summarize_plan(plan),
            "moves": [move.to_dict() for move in plan],
        },
        indent=2,
    )


def format_duplicates(groups: list[DuplicateGroup]) -> str:
    if not groups:
        return "No exact duplicates found."
    lines: list[str] = []
    for index, group in enumerate(groups, start=1):
        lines.append(
            f"Group {index}: {len(group.paths)} files, "
            f"{group.size} bytes each"
        )
        lines.extend(f"  {path}" for path in group.paths)
    reclaimable = sum(group.reclaimable_bytes for group in groups)
    lines.append(
        f"Total: {len(groups)} groups, {reclaimable} reclaimable bytes"
    )
    return "\n".join(lines)


def format_duplicates_json(groups: list[DuplicateGroup]) -> str:
    return json.dumps(
        {
            "total_groups": len(groups),
            "reclaimable_bytes": sum(
                group.reclaimable_bytes for group in groups
            ),
            "groups": [group.to_dict() for group in groups],
        },
        indent=2,
    )


def format_inventory(
    records: list[FileRecord],
    *,
    reference_time: float,
) -> str:
    if not records:
        return "No files matched the inventory filters."
    lines = [
        (
            f"{record.path} [{record.category}] "
            f"{record.size} bytes, "
            f"{record.age_days(reference_time=reference_time)} days old"
        )
        for record in records
    ]
    summary = summarize_inventory(records)
    lines.append(
        f"Total: {summary.total_files} files, {summary.total_bytes} bytes"
    )
    lines.extend(
        f"  {category}: {usage.files} files, {usage.bytes} bytes"
        for category, usage in summary.by_category.items()
    )
    return "\n".join(lines)


def format_inventory_json(
    records: list[FileRecord],
    *,
    reference_time: float,
) -> str:
    summary = summarize_inventory(records)
    return json.dumps(
        {
            **summary.to_dict(),
            "files": [
                record.to_dict(reference_time=reference_time)
                for record in records
            ],
        },
        indent=2,
    )


def format_snapshot_diff(diff: SnapshotDiff) -> str:
    verification = (
        "Verification: SHA-256 contents compared"
        if diff.checksums_compared
        else "Verification: metadata only"
    )
    if not diff.has_changes:
        return (
            f"No changes found. Unchanged: {diff.unchanged}\n"
            f"{verification}"
        )
    lines = [
        (
            f"Changes: {len(diff.added)} added, "
            f"{len(diff.removed)} removed, "
            f"{len(diff.modified)} modified, "
            f"{diff.unchanged} unchanged"
        ),
        verification,
    ]
    lines.extend(f"+ {entry.path}" for entry in diff.added)
    lines.extend(f"- {entry.path}" for entry in diff.removed)
    lines.extend(
        (
            f"~ {change.after.path}: "
            f"{', '.join(change.reasons)} "
            f"({change.before.size} -> {change.after.size} bytes)"
        )
        for change in diff.modified
    )
    return "\n".join(lines)


def format_snapshot_diff_json(diff: SnapshotDiff) -> str:
    return json.dumps(
        {
            "has_changes": diff.has_changes,
            **diff.to_dict(),
        },
        indent=2,
    )


def format_cleanup_review(review: CleanupReview) -> str:
    if not review.candidates:
        return "No cleanup candidates found."
    lines = [
        (
            f"{candidate.path} [{candidate.confidence}] "
            f"{candidate.size} bytes: {', '.join(candidate.reasons)}"
            + (
                f"; keep {candidate.duplicate_of}"
                if candidate.duplicate_of is not None
                else ""
            )
            + (
                f"; {candidate.age_days} days old"
                if candidate.age_days is not None
                else ""
            )
        )
        for candidate in review.candidates
    ]
    lines.append(
        f"Total: {len(review.candidates)} candidates, "
        f"{review.total_candidate_bytes} candidate bytes"
    )
    lines.append(
        f"Exact duplicate reclaimable bytes: "
        f"{review.duplicate_reclaimable_bytes}"
    )
    lines.append("Review only: no files were changed.")
    return "\n".join(lines)


def format_cleanup_review_json(review: CleanupReview) -> str:
    return json.dumps(
        {
            "review_only": True,
            **review.to_dict(),
        },
        indent=2,
    )
