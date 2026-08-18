import shutil

from .planner import Move


def _validate_apply(plan: list[Move]) -> None:
    destinations: set[str] = set()
    for move in plan:
        if not move.source.exists():
            raise FileNotFoundError(f"Source is missing: {move.source}")
        if move.destination.exists():
            raise FileExistsError(f"Destination already exists: {move.destination}")
        key = str(move.destination).casefold()
        if key in destinations:
            raise ValueError(f"Duplicate destination in plan: {move.destination}")
        destinations.add(key)


def apply_plan(plan: list[Move]) -> int:
    _validate_apply(plan)
    completed: list[Move] = []
    try:
        for move in plan:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(move.source), str(move.destination))
            completed.append(move)
    except Exception:
        for move in reversed(completed):
            if move.destination.exists() and not move.source.exists():
                move.source.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(move.destination), str(move.source))
        raise
    return len(completed)


def rollback_plan(plan: list[Move]) -> int:
    for move in plan:
        if not move.destination.exists():
            raise FileNotFoundError(f"Organized file is missing: {move.destination}")
        if move.source.exists():
            raise FileExistsError(f"Original path is occupied: {move.source}")

    restored = 0
    for move in reversed(plan):
        move.source.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(move.destination), str(move.source))
        restored += 1
    return restored
