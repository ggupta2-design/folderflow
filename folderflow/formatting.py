import json

from .analytics import summarize_inventory
from .duplicates import DuplicateGroup
from .inventory import FileRecord
from .planner import Move, summarize_plan


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
