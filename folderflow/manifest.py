import json
from datetime import datetime
from pathlib import Path

from .planner import Move


MANIFEST_VERSION = 1


def write_manifest(plan: list[Move], path: Path, *, root: Path) -> Path:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": MANIFEST_VERSION,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "root": str(root.expanduser().resolve()),
        "moves": [move.to_dict() for move in plan],
    }
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path


def read_manifest(path: Path) -> list[Move]:
    try:
        payload = json.loads(path.expanduser().read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid manifest JSON: {error.msg}") from error

    if payload.get("version") != MANIFEST_VERSION:
        raise ValueError("Unsupported manifest version")
    moves = payload.get("moves")
    if not isinstance(moves, list):
        raise ValueError("Manifest moves must be a list")

    result: list[Move] = []
    for item in moves:
        if not isinstance(item, dict) or not {"source", "destination", "category"} <= set(item):
            raise ValueError("Manifest contains an invalid move")
        result.append(
            Move(
                source=Path(item["source"]),
                destination=Path(item["destination"]),
                category=item["category"],
            )
        )
    return result
