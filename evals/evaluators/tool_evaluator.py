"""Tool-usage evaluation — does the agent call the right tool?

Layer under test::

    question -> router -> (rag | react agent) -> tool usage -> final answer

Evidence for "the tool was used" depends on which branch the router picked:

* ``chat`` branch      — the react agent asks the model for a tool, so the
  tool name shows up in ``message.tool_calls``.
* ``knowledge`` branch — the RAG node calls ``knowledge_search`` directly
  inside the chain, which never produces a ``tool_calls`` entry. The route
  itself is therefore the evidence, because that branch retrieves through
  ``knowledge_search`` by construction.

The agent and the router are only *called* here, never modified.
"""

from __future__ import annotations

from typing import Any

from aila.agent import create_agent
from aila.graph.router import route_question

from evals.utils import (
    EvalOutcome,
    find_missing_keywords,
    format_checklist,
    format_list,
)


# Creating the agent builds an LLM client and opens the vectorstore, so it is
# done once per run and shared by every case.
_AGENT: Any = None


def get_agent() -> Any:
    """Return the compiled agent graph, creating it on first use."""

    global _AGENT

    if _AGENT is None:
        _AGENT = create_agent()

    return _AGENT


def invoke_agent(question: str, case_id: str) -> dict[str, Any]:
    """Run one question through the graph.

    The graph is compiled with a checkpointer, so every call needs a
    ``thread_id``. Each case gets its own thread, otherwise the answer of an
    earlier case leaks into the next one and the run stops being reproducible.

    Args:
        question: The user question.
        case_id: Used to build a per-case memory thread.

    Returns:
        The final graph state.
    """

    config = {"configurable": {"thread_id": f"eval_{case_id}"}}

    return get_agent().invoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
    )


def extract_tool_calls(result: dict[str, Any]) -> list[str]:
    """Extract the tool names the model asked for.

    Args:
        result: Final graph state.

    Returns:
        Tool names in call order (may be empty).
    """

    tool_names: list[str] = []

    for message in result.get("messages", []):
        for tool_call in getattr(message, "tool_calls", None) or []:
            name = tool_call.get("name")

            if name:
                tool_names.append(name)

    return tool_names


def extract_final_response(result: dict[str, Any]) -> str:
    """Extract the text of the last message.

    Args:
        result: Final graph state.

    Returns:
        The assistant answer, or an empty string.
    """

    messages = result.get("messages", [])

    if not messages:
        return ""

    content = getattr(messages[-1], "content", "")

    return "" if content is None else str(content)


def resolve_route(question: str) -> str:
    """Return the branch the graph takes: ``knowledge`` or ``chat``."""

    state = {"messages": [{"role": "user", "content": question}]}

    return route_question(state)


def resolve_used_tools(question: str, result: dict[str, Any]) -> list[str]:
    """Return the tools used by the run, for either graph branch.

    Args:
        question: The user question, used to resolve the route.
        result: Final graph state.

    Returns:
        Tool names; ``["knowledge_search"]`` when the RAG branch was taken
        and no explicit tool call was produced.
    """

    tool_calls = extract_tool_calls(result)

    if tool_calls:
        return tool_calls

    if resolve_route(question) == "knowledge":
        return ["knowledge_search"]

    return []


def evaluate_case(case: dict[str, Any]) -> EvalOutcome:
    """Run one tool-usage case.

    Args:
        case: Dataset entry with ``id``, ``question``, ``expected_tool`` and
            optionally ``forbidden_tool`` / ``response_contains``.

    Returns:
        The outcome, including the route and the tools that were used.
    """

    case_id = str(case.get("id", "unknown"))
    question = str(case.get("question", ""))
    expected_tool = case.get("expected_tool")
    forbidden_tool = case.get("forbidden_tool")
    expected_texts = [str(t) for t in case.get("response_contains", [])]

    if not question:
        return EvalOutcome(case_id, question, False, [], ["question is empty"])

    try:
        result = invoke_agent(question, case_id)
    except Exception as exc:  # an agent crash must fail the case, not the run
        return EvalOutcome(
            case_id, question, False, [], [f"execution error: {exc}"]
        )

    route = resolve_route(question)
    used_tools = resolve_used_tools(question, result)
    answer = extract_final_response(result)
    missing_texts = find_missing_keywords(answer, expected_texts)

    failures: list[str] = []

    # 1. The expected tool must have been used.
    if expected_tool and expected_tool not in used_tools:
        failures.append(f'tool "{expected_tool}" was not called')

    # 2. A forbidden tool must not have been used.
    if forbidden_tool and forbidden_tool in used_tools:
        failures.append(f'tool "{forbidden_tool}" should not have been called')

    # 3. The final answer must satisfy the expected content.
    for text in missing_texts:
        failures.append(f'final response does not contain "{text}"')

    # Any tool other than the expected one is reported as a miss.
    unexpected = [tool for tool in used_tools if tool != expected_tool]

    details = [
        format_list("Route", [route]),
        format_checklist("Tools", used_tools, unexpected),
        format_list("Answer", [answer] if answer.strip() else []),
    ]

    if expected_texts:
        details.append(
            format_checklist("Expected in answer", expected_texts, missing_texts)
        )

    return EvalOutcome(case_id, question, not failures, details, failures)
