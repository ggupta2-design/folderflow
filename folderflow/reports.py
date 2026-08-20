import os
import tempfile
from pathlib import Path


def write_report(
    content: str,
    destination: Path,
    *,
    overwrite: bool = False,
) -> Path:
    destination = destination.expanduser().resolve()
    if not destination.parent.is_dir():
        raise FileNotFoundError(
            f"Report folder does not exist: {destination.parent}"
        )
    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Report already exists: {destination}. Use --force to replace it."
        )

    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()

    return destination
