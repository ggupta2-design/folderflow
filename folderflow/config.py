import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .categories import DEFAULT_CATEGORIES


@dataclass(frozen=True, slots=True)
class Policy:
    categories: Mapping[str, frozenset[str]]
    exclude_patterns: tuple[str, ...] = ()
    min_bytes: int | None = None
    max_bytes: int | None = None

    def __post_init__(self) -> None:
        for label, value in (("min_bytes", self.min_bytes), ("max_bytes", self.max_bytes)):
            if value is not None and (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                raise ValueError(f"{label} must be a non-negative integer")
        if (
            self.min_bytes is not None
            and self.max_bytes is not None
            and self.min_bytes > self.max_bytes
        ):
            raise ValueError("min_bytes cannot exceed max_bytes")


def default_policy() -> Policy:
    return Policy(categories=DEFAULT_CATEGORIES)


def _normalize_categories(value: object) -> dict[str, frozenset[str]]:
    if not isinstance(value, dict) or not value:
        raise ValueError("categories must be a non-empty object")

    result: dict[str, frozenset[str]] = {}
    claimed: dict[str, str] = {}
    for raw_name, raw_extensions in value.items():
        if not isinstance(raw_name, str):
            raise ValueError("category names must be strings")
        name = raw_name.strip()
        if not name or name in {".", ".."} or "/" in name or "\\" in name:
            raise ValueError(f"Unsafe category name: {raw_name!r}")
        if not isinstance(raw_extensions, list) or not raw_extensions:
            raise ValueError(f"Category {name} must contain extensions")

        extensions: set[str] = set()
        for raw_extension in raw_extensions:
            if not isinstance(raw_extension, str):
                raise ValueError("extensions must be strings")
            extension = raw_extension.strip().casefold()
            if not extension.startswith(".") or extension in {".", ".."}:
                raise ValueError(f"Invalid extension: {raw_extension!r}")
            if extension in claimed:
                raise ValueError(
                    f"Extension {extension} is assigned to both "
                    f"{claimed[extension]} and {name}"
                )
            claimed[extension] = name
            extensions.add(extension)
        result[name] = frozenset(extensions)
    return result


def load_policy(path: Path) -> Policy:
    try:
        payload = json.loads(path.expanduser().read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid policy JSON: {error.msg}") from error
    if not isinstance(payload, dict):
        raise ValueError("Policy must be a JSON object")

    allowed = {"categories", "exclude_patterns", "min_bytes", "max_bytes"}
    unknown = set(payload) - allowed
    if unknown:
        raise ValueError(f"Unsupported policy fields: {', '.join(sorted(unknown))}")

    patterns = payload.get("exclude_patterns", [])
    if not isinstance(patterns, list) or not all(
        isinstance(pattern, str) and pattern.strip() for pattern in patterns
    ):
        raise ValueError("exclude_patterns must be a list of non-empty strings")

    categories = (
        _normalize_categories(payload["categories"])
        if "categories" in payload
        else DEFAULT_CATEGORIES
    )
    return Policy(
        categories=categories,
        exclude_patterns=tuple(pattern.strip() for pattern in patterns),
        min_bytes=payload.get("min_bytes"),
        max_bytes=payload.get("max_bytes"),
    )
