"""Shared evaluation helpers.

Layer-agnostic pieces every evaluator needs, so that all three suites return
the same result shape and ``evals/run.py`` can render them with one code path:

* :class:`EvalOutcome`         — the uniform per-case result
* :func:`find_missing_keywords`— the rule-based keyword check
* :func:`format_list`          — ``Title:`` + one line per item
* :func:`format_checklist`     — ``Title:`` + one ``✓``/``✗`` line per item
* :func:`load_dataset`         — re-exported from :mod:`evals.utils.loader`
"""

from __future__ import annotations

from typing import NamedTuple, Sequence

from .loader import DATASETS_DIR, PROJECT_ROOT, load_dataset


__all__ = [
    "DATASETS_DIR",
    "PROJECT_ROOT",
    "EvalOutcome",
    "find_missing_keywords",
    "format_checklist",
    "format_list",
    "load_dataset",
]


class EvalOutcome(NamedTuple):
    """Result of one evaluation case.

    Attributes:
        case_id: Dataset id, e.g. ``"retrieval_001"``.
        question: The question that was evaluated.
        passed: ``True`` when ``failures`` is empty.
        details: Pre-rendered report blocks (``"Keywords:\\n变量 ✓"``).
        failures: Human-readable reasons; empty when the case passed.
    """

    case_id: str
    question: str
    passed: bool
    details: list[str]
    failures: list[str]


def find_missing_keywords(text: str, keywords: Sequence[str]) -> list[str]:
    """Return the keywords that are absent from ``text``.

    Matching is case-insensitive, so ``chunk`` also matches ``Chunks``.

    Args:
        text: Retrieved content or generated answer.
        keywords: Keywords the text is expected to contain.

    Returns:
        The keywords that did not match, in dataset order.
    """

    haystack = text.lower()

    return [
        keyword
        for keyword in keywords
        if keyword.lower() not in haystack
    ]


def format_list(
    title: str,
    items: Sequence[str],
    empty: str = "(none)",
) -> str:
    """Render a titled block with one line per item.

    Args:
        title: Section title, printed with a trailing ``:``.
        items: Lines of the section.
        empty: Placeholder used when ``items`` is empty.

    Returns:
        A single multi-line string.
    """

    lines = [str(item) for item in items] or [empty]

    return "\n".join([f"{title}:", *lines])


def format_checklist(
    title: str,
    items: Sequence[str],
    missing: Sequence[str],
) -> str:
    """Render a titled block with a ``✓``/``✗`` mark per item.

    Args:
        title: Section title, printed with a trailing ``:``.
        items: All items to report.
        missing: The subset of ``items`` that did not match.

    Returns:
        A single multi-line string.
    """

    missed = {str(item) for item in missing}

    marks = [
        f"{item} {'✗' if str(item) in missed else '✓'}"
        for item in items
    ]

    return format_list(title, marks)
