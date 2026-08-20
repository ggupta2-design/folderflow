from pathlib import Path

import pytest

from folderflow.reports import write_report


def test_writes_report_with_trailing_newline(tmp_path: Path) -> None:
    destination = tmp_path / "duplicates.json"

    result = write_report('{"total_groups": 1}', destination)

    assert result == destination
    assert destination.read_text() == '{"total_groups": 1}\n'


def test_refuses_to_overwrite_report_by_default(tmp_path: Path) -> None:
    destination = tmp_path / "duplicates.txt"
    destination.write_text("original")

    with pytest.raises(FileExistsError, match="Use --force"):
        write_report("replacement", destination)

    assert destination.read_text() == "original"


def test_can_atomically_replace_report_when_confirmed(tmp_path: Path) -> None:
    destination = tmp_path / "duplicates.txt"
    destination.write_text("old")

    write_report("new", destination, overwrite=True)

    assert destination.read_text() == "new\n"
    assert list(tmp_path.glob("*.tmp")) == []


def test_requires_existing_destination_folder(tmp_path: Path) -> None:
    destination = tmp_path / "missing" / "report.txt"

    with pytest.raises(FileNotFoundError, match="Report folder"):
        write_report("report", destination)
