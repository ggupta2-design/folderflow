from pathlib import Path

import pytest

from folderflow.duplicates import find_duplicates


def test_finds_only_content_identical_files(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    same_size = tmp_path / "different.txt"
    first.write_text("same")
    second.write_text("same")
    same_size.write_text("diff")

    groups = find_duplicates([first, second, same_size])

    assert len(groups) == 1
    assert groups[0].paths == (first, second)
    assert groups[0].size == 4
    assert groups[0].reclaimable_bytes == 4
    assert len(groups[0].digest) == 64


def test_ignores_unique_files(tmp_path: Path) -> None:
    one = tmp_path / "one.txt"
    two = tmp_path / "two.txt"
    one.write_text("one")
    two.write_text("two")

    assert find_duplicates([one, two]) == []


def test_filters_groups_by_minimum_copy_count(tmp_path: Path) -> None:
    files = [tmp_path / f"copy-{index}.txt" for index in range(3)]
    for path in files:
        path.write_text("same")

    assert find_duplicates(files, minimum_copies=3)[0].paths == tuple(files)
    assert find_duplicates(files, minimum_copies=4) == []


def test_does_not_count_hard_links_twice(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    link = tmp_path / "link.bin"
    copy = tmp_path / "copy.bin"
    source.write_bytes(b"duplicate")
    link.hardlink_to(source)
    copy.write_bytes(b"duplicate")

    groups = find_duplicates([source, link, copy])

    assert len(groups) == 1
    assert len(groups[0].paths) == 2
    assert copy in groups[0].paths


def test_rejects_invalid_options() -> None:
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        find_duplicates([], chunk_size=0)
    with pytest.raises(ValueError, match="minimum_copies must be at least 2"):
        find_duplicates([], minimum_copies=1)
