import json
from pathlib import Path

from folderflow.cli import main


def test_plan_applies_custom_category_policy(
    tmp_path: Path,
    capsys,
) -> None:
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    (downloads / "analysis.ipynb").write_text("{}")
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({
        "categories": {"Notebooks": [".ipynb"]},
    }))

    result = main([
        "plan",
        str(downloads),
        "--config",
        str(policy),
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["summary"] == {"Notebooks": 1}
    assert payload["moves"][0]["destination"].endswith(
        "Notebooks/analysis.ipynb"
    )


def test_plan_combines_policy_and_cli_exclusions(
    tmp_path: Path,
    capsys,
) -> None:
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    (downloads / "keep.pdf").write_text("document")
    (downloads / "ignore.tmp").write_text("temporary")
    (downloads / "empty.pdf").write_text("")
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({
        "exclude_patterns": ["*.tmp"],
        "min_bytes": 1,
    }))

    result = main([
        "plan",
        str(downloads),
        "--config",
        str(policy),
        "--exclude",
        "keep.pdf",
        "--json",
    ])

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["total"] == 0
