from dataclasses import dataclass
from pathlib import Path

from .categories import classify_file


@dataclass(frozen=True, slots=True)
class Move:
    source: Path
    destination: Path
    category: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source": str(self.source),
            "destination": str(self.destination),
            "category": self.category,
        }


def _available_destination(
    directory: Path,
    filename: str,
    reserved: set[str],
) -> Path:
    candidate = directory / filename
    key = str(candidate).casefold()
    if not candidate.exists() and key not in reserved:
        reserved.add(key)
        return candidate

    original = Path(filename)
    counter = 1
    while True:
        candidate = directory / f"{original.stem}-{counter}{original.suffix}"
        key = str(candidate).casefold()
        if not candidate.exists() and key not in reserved:
            reserved.add(key)
            return candidate
        counter += 1


def build_plan(files: list[Path], root: Path) -> list[Move]:
    root = root.expanduser().resolve()
    reserved: set[str] = set()
    plan: list[Move] = []

    for source in files:
        source = source.resolve()
        category = classify_file(source)
        destination_dir = root / category
        if source.parent == destination_dir:
            continue
        destination = _available_destination(destination_dir, source.name, reserved)
        plan.append(Move(source, destination, category))
    return plan


def summarize_plan(plan: list[Move]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for move in plan:
        summary[move.category] = summary.get(move.category, 0) + 1
    return dict(sorted(summary.items()))
