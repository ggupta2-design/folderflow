from pathlib import Path

from folderflow.planner import build_plan, summarize_plan


def test_build_plan_targets_category_folders(tmp_path: Path) -> None:
    report = tmp_path / "report.pdf"
    photo = tmp_path / "photo.jpg"
    report.write_text("report", encoding="utf-8")
    photo.write_text("photo", encoding="utf-8")

    plan = build_plan([report, photo], tmp_path)

    destinations = {move.source.name: move.destination for move in plan}
    assert destinations["report.pdf"] == tmp_path / "Documents" / "report.pdf"
    assert destinations["photo.jpg"] == tmp_path / "Images" / "photo.jpg"


def test_build_plan_avoids_existing_destination(tmp_path: Path) -> None:
    photo = tmp_path / "photo.jpg"
    photo.write_text("new", encoding="utf-8")
    images = tmp_path / "Images"
    images.mkdir()
    (images / "photo.jpg").write_text("existing", encoding="utf-8")

    plan = build_plan([photo], tmp_path)

    assert plan[0].destination == images / "photo-1.jpg"


def test_build_plan_reserves_names_across_multiple_sources(tmp_path: Path) -> None:
    first_dir = tmp_path / "one"
    second_dir = tmp_path / "two"
    first_dir.mkdir()
    second_dir.mkdir()
    first = first_dir / "report.pdf"
    second = second_dir / "report.pdf"
    first.write_text("one", encoding="utf-8")
    second.write_text("two", encoding="utf-8")

    plan = build_plan([first, second], tmp_path)

    assert [move.destination.name for move in plan] == ["report.pdf", "report-1.pdf"]


def test_plan_skips_files_already_organized(tmp_path: Path) -> None:
    documents = tmp_path / "Documents"
    documents.mkdir()
    report = documents / "report.pdf"
    report.write_text("report", encoding="utf-8")

    assert build_plan([report], tmp_path) == []


def test_summarize_plan_counts_categories(tmp_path: Path) -> None:
    files = [tmp_path / "a.pdf", tmp_path / "b.pdf", tmp_path / "c.jpg"]
    for path in files:
        path.write_text(path.name, encoding="utf-8")

    assert summarize_plan(build_plan(files, tmp_path)) == {
        "Documents": 2,
        "Images": 1,
    }


def test_build_plan_uses_custom_categories(tmp_path: Path) -> None:
    notebook = tmp_path / "analysis.ipynb"
    notebook.write_text("{}", encoding="utf-8")

    plan = build_plan(
        [notebook],
        tmp_path,
        categories={"Notebooks": frozenset({".ipynb"})},
    )

    assert plan[0].category == "Notebooks"
    assert plan[0].destination == tmp_path / "Notebooks" / "analysis.ipynb"
