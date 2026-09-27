"""RAG answer evaluation — is the answer grounded in the knowledge base?

Layer under test::

    question -> create_rag_chain() -> knowledge_search + LLM -> answer

Phase 1 is **rule based** on purpose: no LLM-as-judge, so the result is
deterministic, free and fast. Checks:

    1. the answer is not empty
    2. every expected keyword appears in the answer
    3. no obvious failure marker (refusal / "nothing found" style answer)

The RAG chain is only *called* here, never modified.
"""

from __future__ import annotations

from typing import Any, Sequence

from aila.rag import create_rag_chain

from evals.utils import (
    EvalOutcome,
    find_missing_keywords,
    format_checklist,
    format_list,
)


# Rule-based "obvious error" markers. A grounded answer is generated from
# retrieved chunks, so it must never be a refusal or an empty-knowledge
# fallback such as the one ``knowledge_search`` returns when nothing matched.
FORBIDDEN_PATTERNS: tuple[str, ...] = (
    "我不知道",
    "无法回答",
    "没有找到相关",
    "no relevant documents found",
    "as an ai",
    "i don't know",
)


# Building the chain creates an LLM client, so it is done once per run.
_CHAIN: Any = None


def get_chain() -> Any:
    """Return the RAG chain, creating it on first use."""

    global _CHAIN

    if _CHAIN is None:
        _CHAIN = create_rag_chain()

    return _CHAIN


def find_forbidden_patterns(answer: str, patterns: Sequence[str]) -> list[str]:
    """Return the failure markers that appear in ``answer``.

    Args:
        answer: Generated answer text.
        patterns: Markers that must not appear.

    Returns:
        The markers that did appear, case-insensitively matched.
    """

    haystack = answer.lower()

    return [
        pattern
        for pattern in patterns
        if pattern.lower() in haystack
    ]


def evaluate_case(case: dict[str, Any]) -> EvalOutcome:
    """Run one RAG answer case.

    Args:
        case: Dataset entry with ``id``, ``question``, ``expected_keywords``
            and optionally ``forbidden_patterns``.

    Returns:
        The outcome, including the answer and the keyword hits.
    """

    case_id = str(case.get("id", "unknown"))
    question = str(case.get("question", ""))
    expected_keywords = [str(k) for k in case.get("expected_keywords", [])]
    forbidden = case.get("forbidden_patterns", FORBIDDEN_PATTERNS)

    if not question:
        return EvalOutcome(case_id, question, False, [], ["question is empty"])

    try:
        answer = str(get_chain().invoke(question))
    except Exception as exc:  # a broken chain must fail the case, not the run
        return EvalOutcome(
            case_id, question, False, [], [f"execution error: {exc}"]
        )

    missing = find_missing_keywords(answer, expected_keywords)
    hits = find_forbidden_patterns(answer, forbidden)

    failures: list[str] = []

    # 1. The chain must produce an answer at all.
    if not answer.strip():
        failures.append("answer is empty")

    # 2. The answer must cover what the knowledge base says about it.
    for keyword in missing:
        failures.append(f'answer does not contain "{keyword}"')

    # 3. The answer must not be a refusal or an empty-knowledge fallback.
    for pattern in hits:
        failures.append(f'answer contains the failure marker "{pattern}"')

    details = [
        format_list("Answer", [answer] if answer.strip() else []),
        format_checklist("Keywords", expected_keywords, missing),
    ]

    return EvalOutcome(case_id, question, not failures, details, failures)
