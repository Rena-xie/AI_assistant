"""Retrieval evaluation — is the right content retrieved?

Layer under test (no agent, no LLM generation)::

    question -> knowledge_search.invoke() -> retrieved chunks

Checks:
    1. the tool returns non-empty content
    2. every result carries a ``Source:`` line
    3. the expected keywords are present in the retrieved text

Migrated from ``evals/run_retrieval_eval.py``, which is kept for backward
compatibility and still runs on ``datasets/rag_retrieval.json``.
"""

from __future__ import annotations

import re
from typing import Any

from aila.tools.knowledge_search import knowledge_search

from evals.utils import (
    EvalOutcome,
    find_missing_keywords,
    format_checklist,
    format_list,
)


# ``knowledge_search`` renders each chunk as "Source:" followed by the path.
SOURCE_PATTERN = re.compile(r"Source:\s*\n\s*(.+)")


def extract_sources(result: str) -> list[str]:
    """Extract the unique source paths from a tool result.

    Args:
        result: Raw string returned by ``knowledge_search``.

    Returns:
        Source paths in order of appearance, without duplicates.
    """

    sources: list[str] = []

    for match in SOURCE_PATTERN.finditer(result):
        source = match.group(1).strip()

        if source and source not in sources:
            sources.append(source)

    return sources


def evaluate_case(case: dict[str, Any]) -> EvalOutcome:
    """Run one retrieval case.

    Args:
        case: Dataset entry with ``id``, ``question`` and
            ``expected_keywords``.

    Returns:
        The outcome, including the retrieved sources and keyword hits.
    """

    case_id = str(case.get("id", "unknown"))
    question = str(case.get("question", ""))
    expected_keywords = [str(k) for k in case.get("expected_keywords", [])]

    if not question:
        return EvalOutcome(case_id, question, False, [], ["question is empty"])

    try:
        result = knowledge_search.invoke(question)
    except Exception as exc:  # a broken retriever must fail the case, not the run
        return EvalOutcome(
            case_id, question, False, [], [f"execution error: {exc}"]
        )

    sources = extract_sources(result)
    missing = find_missing_keywords(result, expected_keywords)

    failures: list[str] = []

    # 1. Something must come back at all.
    if not result.strip():
        failures.append("retrieval result is empty")

    # 2. Every chunk must be traceable to a document.
    if not sources:
        failures.append("no 'Source:' found in the retrieval result")

    # 3. The retrieved text must cover the expected keywords.
    for keyword in missing:
        failures.append(f'keyword "{keyword}" was not retrieved')

    details = [
        format_list("Retrieved", sources),
        format_checklist("Keywords", expected_keywords, missing),
    ]

    return EvalOutcome(case_id, question, not failures, details, failures)
