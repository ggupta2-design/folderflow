import json
import os
from pathlib import Path
from time import time

from folderflow.cli import build_parser, main


def test_review_parser_accepts_cleanup_options() -> None:
    args = build_parser().parse_args([
        "review",
        "downloads",
        "--older-than-days",
        "60",
        "--minimum-copies",
        "3",
        "--json",
    ])

    assert args.command == "review"
    assert args.root == Path("downloads")
    assert args.older_than_days == 60
    assert args.minimum_copies == 3
    assert args.as_json


def test_review_command_combines_stale_and_duplicate_findings(
    tmp_path: Path,
    capsys,
) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_text("same")
    second.write_text("same")
    old_time = time() - 120 * 86400
    os.utime(first, (old_time, old_time))
    os.utime(second, (old_time, old_time))

    result = main([
        "review",
        str(tmp_path),
        "--older-than-days",
        "90",
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    candidates = {
        Path(item["path"]).name: item
        for item in payload["candidates"]
    }
    assert result == 0
    assert payload["review_only"]
    assert payload["total_candidates"] == 2
    assert candidates["a.txt"]["reasons"] == ["stale"]
    assert candidates["b.txt"]["reasons"] == ["duplicate", "stale"]
    assert payload["duplicate_reclaimable_bytes"] == 4


def test_review_command_can_skip_duplicate_hashing(
    tmp_path: Path,
    capsys,
) -> None:
    (tmp_path / "a.txt").write_text("same")
    (tmp_path / "b.txt").write_text("same")

    result = main([
        "review",
        str(tmp_path),
        "--older-than-days",
        "365",
        "--no-duplicates",
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["total_candidates"] == 0


def test_review_command_exports_without_self_inclusion(
    tmp_path: Path,
    capsys,
) -> None:
    output = tmp_path / "review.json"
    output.write_text("old report")

    result = main([
        "review",
        str(tmp_path),
        "--older-than-days",
        "365",
        "--no-duplicates",
        "--json",
        "--output",
        str(output),
        "--force",
    ])

    message = capsys.readouterr().out
    payload = json.loads(output.read_text())
    assert result == 0
    assert "Cleanup review written to" in message
    assert payload["total_candidates"] == 0


def test_review_command_uses_custom_policy_categories(
    tmp_path: Path,
    capsys,
) -> None:
    notebook = tmp_path / "analysis.ipynb"
    notebook.write_text("{}")
    old_time = time() - 120 * 86400
    os.utime(notebook, (old_time, old_time))
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({
        "categories": {"Notebooks": [".ipynb"]},
        "exclude_patterns": ["policy.json"],
    }))

    result = main([
        "review",
        str(tmp_path),
        "--config",
        str(policy),
        "--older-than-days",
        "90",
        "--no-duplicates",
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["candidates"][0]["category"] == "Notebooks"
