from pathlib import Path

import pytest

from folderflow.executor import apply_plan, rollback_plan
from folderflow.manifest import read_manifest, write_manifest
from folderflow.planner import Move


def test_apply_and_rollback_round_trip(tmp_path: Path) -> None:
    source = tmp_path / "report.pdf"
    source.write_text("report", encoding="utf-8")
    destination = tmp_path / "Documents" / "report.pdf"
    plan = [Move(source, destination, "Documents")]

    assert apply_plan(plan) == 1
    assert destination.read_text(encoding="utf-8") == "report"
    assert not source.exists()

    assert rollback_plan(plan) == 1
    assert source.read_text(encoding="utf-8") == "report"
    assert not destination.exists()


def test_apply_refuses_to_overwrite_destination(tmp_path: Path) -> None:
    source = tmp_path / "photo.jpg"
    destination = tmp_path / "Images" / "photo.jpg"
    destination.parent.mkdir()
    source.write_text("new", encoding="utf-8")
    destination.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        apply_plan([Move(source, destination, "Images")])

    assert source.read_text(encoding="utf-8") == "new"
    assert destination.read_text(encoding="utf-8") == "existing"


def test_rollback_refuses_to_overwrite_original_path(tmp_path: Path) -> None:
    source = tmp_path / "report.pdf"
    destination = tmp_path / "Documents" / "report.pdf"
    destination.parent.mkdir()
    source.write_text("replacement", encoding="utf-8")
    destination.write_text("organized", encoding="utf-8")

    with pytest.raises(FileExistsError):
        rollback_plan([Move(source, destination, "Documents")])


def test_manifest_round_trip(tmp_path: Path) -> None:
    move = Move(
        tmp_path / "report.pdf",
        tmp_path / "Documents" / "report.pdf",
        "Documents",
    )
    path = tmp_path / "manifests" / "run.json"

    written = write_manifest([move], path, root=tmp_path)

    assert written == path
    assert read_manifest(path) == [move]
    assert not path.with_suffix(".json.tmp").exists()


def test_manifest_rejects_unknown_version(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    path.write_text('{"version": 99, "moves": []}', encoding="utf-8")

    with pytest.raises(ValueError, match="version"):
        read_manifest(path)
