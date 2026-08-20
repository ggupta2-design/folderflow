import json

from .duplicates import DuplicateGroup
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
