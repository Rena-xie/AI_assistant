"""Retrieval-level evaluation.

This script evaluates the **retriever** only: it calls the
``knowledge_search`` tool directly and never invokes the agent.

Chain under test::

    question -> similarity_search() -> retrieved chunks

Usage::

    python evals/run_retrieval_eval.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from aila.tools.knowledge_search import knowledge_search


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "evals" / "datasets" / "rag_retrieval.json"

# ``knowledge_search`` prints "Source:" followed by the file path.
SOURCE_PATTERN = re.compile(r"Source:\s*\n\s*(.+)")


def load_dataset(path: Path) -> list[dict[str, Any]]:
    """Load retrieval cases from a JSON dataset."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Retrieval dataset must be a JSON list.")

    return data


def extract_sources(result: str) -> list[str]:
    """Extract unique source paths from the tool output."""
    sources: list[str] = []

    for match in SOURCE_PATTERN.finditer(result):
        source = match.group(1).strip()

        if source and source not in sources:
            sources.append(source)

    return sources


def find_missing_keywords(
    result: str,
    expected_keywords: list[str],
) -> list[str]:
    """Return the expected keywords that are absent from the result.

    Matching is case-insensitive so that ``chunk`` also matches
    ``Chunks`` and ``key-value`` also matches ``Key-Value``.
    """
    haystack = result.lower()

    return [
        keyword
        for keyword in expected_keywords
        if keyword.lower() not in haystack
    ]


def evaluate_case(
    case: dict[str, Any],
) -> tuple[bool, str, list[str], list[str]]:
    """Run one retrieval case.

    Returns:
        (passed, result, sources, missing_keywords)
    """
    question = case.get("question", "")
    expected_keywords = case.get("expected_keywords", [])

    if not question:
        return False, "", [], ["question is empty"]

    result = knowledge_search.invoke(question)

    sources = extract_sources(result)
    missing = find_missing_keywords(result, expected_keywords)

    passed = len(missing) == 0

    return passed, result, sources, missing


def main() -> None:
    dataset = load_dataset(DATASET_PATH)

    total = len(dataset)
    passed_count = 0

    print("=" * 50)
    print("RAG Retrieval Evaluation")
    print("=" * 50)

    for case in dataset:
        case_id = case.get("id", "unknown")
        question = case.get("question", "")
        expected_keywords = case.get("expected_keywords", [])

        try:
            passed, result, sources, missing = evaluate_case(case)
        except Exception as exc:
            passed = False
            sources = []
            missing = [f"execution error: {exc}"]

        if passed:
            passed_count += 1

        print()
        print(f"[{'PASS' if passed else 'FAIL'}] {case_id}")
        print()
        print("Question:")
        print(question)
        print()
        print("Retrieved:")

        if sources:
            for source in sources:
                print(source)
        else:
            print("(no source)")

        if passed:
            print()
            print("Keywords:")
            for keyword in expected_keywords:
                print(keyword)
        else:
            print()
            print("Missing:")
            for keyword in missing:
                print(keyword)

        print()
        print("-" * 20)

    print()
    print("=" * 50)
    print("Result:")
    print(f"{passed_count}/{total} passed")
    print("=" * 50)

    if passed_count != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()