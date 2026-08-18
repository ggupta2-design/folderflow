import json

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
