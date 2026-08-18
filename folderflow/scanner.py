from pathlib import Path


def _is_hidden(path: Path, root: Path) -> bool:
    return any(part.startswith(".") for part in path.relative_to(root).parts)


def scan_files(
    root: Path,
    *,
    recursive: bool = False,
    include_hidden: bool = False,
) -> list[Path]:
    root = root.expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Folder does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Not a folder: {root}")

    candidates = root.rglob("*") if recursive else root.iterdir()
    files = [
        path
        for path in candidates
        if path.is_file()
        and not path.is_symlink()
        and (include_hidden or not _is_hidden(path, root))
    ]
    return sorted(files, key=lambda path: path.relative_to(root).as_posix().casefold())
