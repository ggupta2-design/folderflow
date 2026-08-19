from fnmatch import fnmatch
from pathlib import Path


def _is_hidden(path: Path, root: Path) -> bool:
    return any(part.startswith(".") for part in path.relative_to(root).parts)


def _is_excluded(path: Path, root: Path, patterns: tuple[str, ...]) -> bool:
    relative = path.relative_to(root).as_posix()
    return any(
        fnmatch(relative, pattern) or fnmatch(path.name, pattern)
        for pattern in patterns
    )


def _within_size(
    path: Path,
    min_bytes: int | None,
    max_bytes: int | None,
) -> bool:
    size = path.stat().st_size
    if min_bytes is not None and size < min_bytes:
        return False
    if max_bytes is not None and size > max_bytes:
        return False
    return True


def scan_files(
    root: Path,
    *,
    recursive: bool = False,
    include_hidden: bool = False,
    exclude_patterns: tuple[str, ...] = (),
    min_bytes: int | None = None,
    max_bytes: int | None = None,
) -> list[Path]:
    root = root.expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Folder does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Not a folder: {root}")
    if min_bytes is not None and min_bytes < 0:
        raise ValueError("min_bytes must be non-negative")
    if max_bytes is not None and max_bytes < 0:
        raise ValueError("max_bytes must be non-negative")
    if (
        min_bytes is not None
        and max_bytes is not None
        and min_bytes > max_bytes
    ):
        raise ValueError("min_bytes cannot exceed max_bytes")

    candidates = root.rglob("*") if recursive else root.iterdir()
    files = [
        path
        for path in candidates
        if path.is_file()
        and not path.is_symlink()
        and (include_hidden or not _is_hidden(path, root))
        and not _is_excluded(path, root, exclude_patterns)
        and _within_size(path, min_bytes, max_bytes)
    ]
    return sorted(files, key=lambda path: path.relative_to(root).as_posix().casefold())
