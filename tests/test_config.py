import json
from pathlib import Path

import pytest

from folderflow.config import default_policy, load_policy


def test_default_policy_contains_builtin_categories() -> None:
    policy = default_policy()

    assert ".pdf" in policy.categories["Documents"]
    assert policy.exclude_patterns == ()


def test_load_policy_normalizes_custom_categories(tmp_path: Path) -> None:
    path = tmp_path / "policy.json"
    path.write_text(json.dumps({
        "categories": {
            "School": [".PDF", ".ipynb"],
            "Photos": [".jpg"],
        },
        "exclude_patterns": ["drafts/**", "*.tmp"],
        "min_bytes": 10,
        "max_bytes": 1000,
    }), encoding="utf-8")

    policy = load_policy(path)

    assert policy.categories["School"] == frozenset({".pdf", ".ipynb"})
    assert policy.exclude_patterns == ("drafts/**", "*.tmp")
    assert policy.min_bytes == 10
    assert policy.max_bytes == 1000


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"unknown": True},
        {"categories": {}},
        {"categories": {"../escape": [".txt"]}},
        {"categories": {"One": ["txt"]}},
        {"categories": {"One": [".txt"], "Two": [".TXT"]}},
        {"exclude_patterns": "drafts/**"},
        {"min_bytes": -1},
        {"min_bytes": 100, "max_bytes": 10},
    ],
)
def test_load_policy_rejects_invalid_or_unsafe_values(
    tmp_path: Path,
    payload: object,
) -> None:
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError):
        load_policy(path)
