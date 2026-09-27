"""Dataset loading for the evaluation suites.

Single responsibility: turn ``evals/datasets/<name>.json`` into a validated
list of case dicts. Reporting and grading live elsewhere.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EVALS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EVALS_DIR.parent
DATASETS_DIR = EVALS_DIR / "datasets"


def resolve_dataset_path(name: str) -> Path:
    """Return the path of ``<name>.json``, raising when it does not exist.

    Args:
        name: Suite name, e.g. ``"retrieval"``.

    Returns:
        Absolute path of the dataset file.
    """

    path = DATASETS_DIR / f"{name}.json"

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    return path


def validate_cases(data: Any, path: Path) -> list[dict[str, Any]]:
    """Check the dataset shape and fail loudly on malformed cases.

    A dataset is a JSON list of objects; every object needs an ``id`` and a
    ``question``, because both are required to report a result.

    Args:
        data: Parsed JSON content.
        path: Dataset path, only used for error messages.

    Returns:
        The validated list of cases.
    """

    if not isinstance(data, list):
        raise ValueError(f"Dataset must be a JSON list: {path}")

    for index, case in enumerate(data):
        if not isinstance(case, dict):
            raise ValueError(f"{path.name} case #{index} must be a JSON object")

        if not case.get("id"):
            raise ValueError(f"{path.name} case #{index} is missing an 'id'")

        if not case.get("question"):
            raise ValueError(f"{path.name} case #{index} is missing a 'question'")

    return data


def load_dataset(name: str) -> list[dict[str, Any]]:
    """Load and validate one evaluation dataset.

    Args:
        name: Suite name, e.g. ``"rag"``.

    Returns:
        The evaluation cases as a list of dicts.
    """

    path = resolve_dataset_path(name)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return validate_cases(data, path)
