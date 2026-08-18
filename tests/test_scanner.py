from pathlib import Path

import pytest

from folderflow.categories import classify_file
from folderflow.scanner import scan_files


@pytest.mark.parametrize(
    ("filename", "category"),
    [
        ("report.PDF", "Documents"),
        ("photo.jpg", "Images"),
        ("song.mp3", "Audio"),
        ("clip.mp4", "Video"),
        ("bundle.zip", "Archives"),
        ("script.py", "Code"),
        ("budget.xlsx", "Spreadsheets"),
        ("LICENSE", "Other"),
    ],
)
def test_classify_file(filename: str, category: str) -> None:
    assert classify_file(Path(filename)) == category


def test_scan_files_is_sorted_and_non_recursive_by_default(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "c.txt").write_text("c", encoding="utf-8")

    files = scan_files(tmp_path)

    assert [path.name for path in files] == ["a.txt", "b.txt"]


def test_recursive_scan_excludes_hidden_files(tmp_path: Path) -> None:
    visible = tmp_path / "nested"
    visible.mkdir()
    (visible / "report.pdf").write_text("report", encoding="utf-8")
    (tmp_path / ".secret.txt").write_text("secret", encoding="utf-8")

    files = scan_files(tmp_path, recursive=True)

    assert [path.name for path in files] == ["report.pdf"]


def test_scan_can_include_hidden_files(tmp_path: Path) -> None:
    hidden = tmp_path / ".notes.txt"
    hidden.write_text("notes", encoding="utf-8")

    assert scan_files(tmp_path, include_hidden=True) == [hidden]


def test_scan_rejects_missing_folder(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        scan_files(tmp_path / "missing")
