from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aila.agent import create_agent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "evals" / "datasets" / "basic_agent.json"


def load_dataset(path: Path) -> list[dict[str, Any]]:
    """Load evaluation cases from a JSON dataset."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Evaluation dataset must be a JSON list.")

    return data


def extract_final_response(result: dict[str, Any]) -> str:
    """Extract the final assistant response."""
    messages = result.get("messages", [])

    if not messages:
        return ""

    last_message = messages[-1]

    content = getattr(last_message, "content", "")

    if content is None:
        return ""

    return str(content)


def extract_tool_calls(result: dict[str, Any]) -> list[str]:
    """Extract tool names used during the agent execution."""
    messages = result.get("messages", [])

    tool_names: list[str] = []

    for message in messages:
        tool_calls = getattr(message, "tool_calls", None)

        if not tool_calls:
            continue

        for tool_call in tool_calls:
            name = tool_call.get("name")

            if name:
                tool_names.append(name)

    return tool_names


def evaluate_case(
    agent: Any,
    case: dict[str, Any],
) -> tuple[bool, list[str]]:
    """
    Run one evaluation case.

    Returns:
        (passed, failure_reasons)
    """
    question = case.get("question", "")
    checks = case.get("checks", {})

    if not question:
        return False, ["question is empty"]

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    final_response = extract_final_response(result)
    tool_calls = extract_tool_calls(result)

    failures: list[str] = []

    # 1. Final response must not be empty.
    if checks.get("response_non_empty"):
        if not final_response.strip():
            failures.append("final response is empty")

    # 2. Final response must contain expected text.
    expected_texts = checks.get("response_contains", [])

    for expected_text in expected_texts:
        if expected_text not in final_response:
            failures.append(
                f'final response does not contain "{expected_text}"'
            )

    # 3. A specific tool must be called.
    expected_tool = checks.get("tool_called")

    if expected_tool:
        if expected_tool not in tool_calls:
            failures.append(
                f'tool "{expected_tool}" was not called'
            )

    # 4. A specific tool must NOT be called.
    forbidden_tool = checks.get("tool_not_called")

    if forbidden_tool:
        if forbidden_tool in tool_calls:
            failures.append(
                f'tool "{forbidden_tool}" should not have been called'
            )

    passed = len(failures) == 0

    return passed, failures


def main() -> None:
    dataset = load_dataset(DATASET_PATH)

    agent = create_agent()

    total = len(dataset)
    passed_count = 0

    print("=" * 60)
    print("AI Learning Assistant - Evaluation")
    print("=" * 60)

    for case in dataset:
        case_id = case.get("id", "unknown")
        question = case.get("question", "")

        try:
            passed, failures = evaluate_case(agent, case)
        except Exception as exc:
            passed = False
            failures = [f"execution error: {exc}"]

        if passed:
            passed_count += 1
            print(f"\n[PASS] {case_id}")
        else:
            print(f"\n[FAIL] {case_id}")

            for failure in failures:
                print(f"       - {failure}")

        print(f"       question: {question}")

    print("\n" + "=" * 60)
    print(f"Result: {passed_count}/{total} passed")
    print("=" * 60)

    if passed_count != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()