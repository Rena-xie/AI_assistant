"""Tests for the evaluation framework under ``evals/``.

Coverage:
    1. the eval modules can be imported
    2. the datasets can be loaded and are well formed
    3. every evaluator can run — offline against fakes, plus one real
       retrieval case against the persisted vectorstore
    4. ``evals/run.py`` renders the unified report and survives bad input

The offline cases patch the seams the evaluators expose (``knowledge_search``,
``get_chain``, ``get_agent``), so no LLM or embedding call is needed and the
result is deterministic.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ``evals`` is not an installed distribution, so the project root has to be
# importable before the eval modules can be loaded.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals import run as eval_run
from evals.evaluators import (
    answer_evaluator,
    retrieval_evaluator,
    tool_evaluator,
)
from evals.utils import EvalOutcome, find_missing_keywords, load_dataset


SUITES = ("retrieval", "rag", "agent")

RETRIEVAL_RESULT = """
Source:
knowledge/documents/learning_notes/数据类型与变量.md

Content:
变量只是指向内存中对象的引用。
"""


class FakeTool:
    """Stand-in for the ``knowledge_search`` tool."""

    def __init__(self, result: str) -> None:
        self.result = result
        self.queries: list[str] = []

    def invoke(self, query: str) -> str:
        self.queries.append(query)

        return self.result


class FakeChain:
    """Stand-in for the RAG chain."""

    def __init__(self, answer: str) -> None:
        self.answer = answer
        self.questions: list[str] = []

    def invoke(self, question: str) -> str:
        self.questions.append(question)

        return self.answer


class FakeAgent:
    """Stand-in for the compiled LangGraph agent."""

    def __init__(self, messages: list[Any]) -> None:
        self.messages = messages
        self.configs: list[Any] = []

    def invoke(
        self,
        payload: dict[str, Any],
        config: Any = None,
    ) -> dict[str, Any]:
        self.configs.append(config)

        return {"messages": self.messages}


def message(content: str, tool_calls: Any = None) -> SimpleNamespace:
    """Build a minimal message object with the attributes evaluators read."""

    return SimpleNamespace(content=content, tool_calls=tool_calls)


# ---------------------------------------------------------------- 1. imports


def test_eval_modules_import():
    """1. Every module exposes the API ``run.py`` relies on."""

    assert callable(retrieval_evaluator.evaluate_case)
    assert callable(answer_evaluator.evaluate_case)
    assert callable(tool_evaluator.evaluate_case)
    assert callable(eval_run.main)

    assert set(eval_run.SUITES) == set(SUITES)


# ---------------------------------------------------------------- 2. datasets


def test_datasets_load():
    """2. Each suite has a loadable, well-formed dataset."""

    for suite in SUITES:
        cases = load_dataset(suite)

        assert cases, f"{suite}.json should not be empty"

        ids = [case["id"] for case in cases]
        assert len(ids) == len(set(ids)), f"{suite}.json ids must be unique"

        for case in cases:
            assert str(case["question"]).strip(), f"{case['id']} needs a question"


def test_dataset_expectations_match_suite():
    """2. retrieval/rag grade keywords, agent grades tool usage."""

    for suite in ("retrieval", "rag"):
        for case in load_dataset(suite):
            assert case.get("expected_keywords"), f"{case['id']} needs keywords"

    for case in load_dataset("agent"):
        assert case.get("expected_tool"), f"{case['id']} needs an expected_tool"


def test_load_dataset_rejects_unknown_suite():
    """2. A missing dataset fails loudly instead of running zero cases."""

    with pytest.raises(FileNotFoundError):
        load_dataset("does_not_exist")


def test_find_missing_keywords_is_case_insensitive():
    """2. The shared keyword rule is case-insensitive."""

    assert find_missing_keywords("Chunks and RAG", ["chunk", "rag"]) == []
    assert find_missing_keywords("only text", ["chunk"]) == ["chunk"]


# ------------------------------------------------------- 3. retrieval evaluator


def test_retrieval_evaluator_passes(monkeypatch):
    """3. A good tool result passes and reports sources plus keyword hits."""

    tool = FakeTool(RETRIEVAL_RESULT)
    monkeypatch.setattr(retrieval_evaluator, "knowledge_search", tool)

    outcome = retrieval_evaluator.evaluate_case(
        {
            "id": "retrieval_001",
            "question": "Python中的变量本质是什么？",
            "expected_keywords": ["变量", "内存", "引用"],
        }
    )

    assert isinstance(outcome, EvalOutcome)
    assert outcome.passed, outcome.failures
    assert outcome.failures == []

    assert tool.queries == ["Python中的变量本质是什么？"]
    assert any("数据类型与变量.md" in block for block in outcome.details)
    assert any("变量 ✓" in block for block in outcome.details)


def test_retrieval_evaluator_reports_missing_keyword(monkeypatch):
    """3. A keyword that was not retrieved fails the case and is marked."""

    tool = FakeTool("Source:\na.md\n\nContent:\n变量指向内存中的对象。")
    monkeypatch.setattr(retrieval_evaluator, "knowledge_search", tool)

    outcome = retrieval_evaluator.evaluate_case(
        {
            "id": "retrieval_x",
            "question": "Python中的变量本质是什么？",
            "expected_keywords": ["变量", "引用"],
        }
    )

    assert not outcome.passed
    assert any('"引用"' in failure for failure in outcome.failures)
    assert any("引用 ✗" in block for block in outcome.details)


def test_retrieval_evaluator_fails_without_source(monkeypatch):
    """3. An empty-knowledge tool result fails the source check."""

    tool = FakeTool("No relevant documents found.")
    monkeypatch.setattr(retrieval_evaluator, "knowledge_search", tool)

    outcome = retrieval_evaluator.evaluate_case(
        {
            "id": "retrieval_y",
            "question": "完全不相关的问题",
            "expected_keywords": ["变量"],
        }
    )

    assert not outcome.passed
    assert "no 'Source:' found in the retrieval result" in outcome.failures


def test_retrieval_evaluator_runs_against_real_vectorstore():
    """3. End-to-end wiring: a real dataset case runs against Chroma.

    Requires the paid DashScope embedding API. When the account is in arrears
    or the API is unreachable the test skips instead of failing, so the
    off-line suite stays green without a live embedding API (same rule as
    LangSmith: no key -> no impact on local runs).
    """

    case = load_dataset("retrieval")[0]

    outcome = retrieval_evaluator.evaluate_case(case)

    assert outcome.case_id == case["id"]
    assert outcome.question == case["question"]

    if outcome.failures and any(
        "execution error" in failure for failure in outcome.failures
    ):
        pytest.skip(f"embedding API unavailable: {outcome.failures[0]}")

    assert outcome.passed, outcome.failures


# ---------------------------------------------------------- 3. answer evaluator


def test_answer_evaluator_passes(monkeypatch):
    """3. A grounded answer containing every keyword passes."""

    chain = FakeChain("tuple 一旦创建就不可变，因此共享数据时更安全。")
    monkeypatch.setattr(answer_evaluator, "get_chain", lambda: chain)

    outcome = answer_evaluator.evaluate_case(
        {
            "id": "rag_001",
            "question": "Python中的tuple为什么不可变？",
            "expected_keywords": ["不可变", "安全"],
        }
    )

    assert outcome.passed, outcome.failures
    assert chain.questions == ["Python中的tuple为什么不可变？"]
    assert any("不可变 ✓" in block for block in outcome.details)


def test_answer_evaluator_flags_missing_keyword(monkeypatch):
    """3. An answer that ignores the knowledge base fails."""

    chain = FakeChain("tuple 是一种序列类型。")
    monkeypatch.setattr(answer_evaluator, "get_chain", lambda: chain)

    outcome = answer_evaluator.evaluate_case(
        {
            "id": "rag_x",
            "question": "Python中的tuple为什么不可变？",
            "expected_keywords": ["不可变", "安全"],
        }
    )

    assert not outcome.passed
    assert len(outcome.failures) == 2
    assert any("不可变" in failure for failure in outcome.failures)


def test_answer_evaluator_flags_refusal(monkeypatch):
    """3. A refusal is an obvious error marker and fails the case."""

    chain = FakeChain("抱歉，我不知道这个问题的答案。")
    monkeypatch.setattr(answer_evaluator, "get_chain", lambda: chain)

    outcome = answer_evaluator.evaluate_case(
        {
            "id": "rag_y",
            "question": "Python中的tuple为什么不可变？",
            "expected_keywords": [],
        }
    )

    assert not outcome.passed
    assert any("failure marker" in failure for failure in outcome.failures)


def test_answer_evaluator_flags_empty_answer(monkeypatch):
    """3. An empty answer fails even without keywords."""

    chain = FakeChain("   ")
    monkeypatch.setattr(answer_evaluator, "get_chain", lambda: chain)

    outcome = answer_evaluator.evaluate_case(
        {"id": "rag_z", "question": "Python中的变量本质是什么？"}
    )

    assert not outcome.passed
    assert "answer is empty" in outcome.failures


# ------------------------------------------------------------ 3. tool evaluator


def test_tool_evaluator_detects_calculator(monkeypatch):
    """3. Chat route: the tool name comes from ``message.tool_calls``."""

    messages = [
        message("123*456是多少？"),
        message("", [{"name": "calculator", "args": {"expression": "123*456"}}]),
        message("56088"),
    ]
    agent = FakeAgent(messages)
    monkeypatch.setattr(tool_evaluator, "get_agent", lambda: agent)

    outcome = tool_evaluator.evaluate_case(
        {
            "id": "tool_001",
            "question": "123*456是多少？",
            "expected_tool": "calculator",
            "response_contains": ["56088"],
        }
    )

    assert outcome.passed, outcome.failures
    assert tool_evaluator.extract_tool_calls({"messages": messages}) == ["calculator"]
    assert tool_evaluator.extract_final_response({"messages": messages}) == "56088"

    # Every case runs on its own memory thread, or answers leak across cases.
    assert agent.configs[0]["configurable"]["thread_id"] == "eval_tool_001"


def test_tool_evaluator_accepts_rag_route_as_knowledge_search(monkeypatch):
    """3. Knowledge route: RAG calls ``knowledge_search`` inside the chain."""

    agent = FakeAgent(
        [
            message("Python中的tuple为什么不可变？"),
            message("tuple 不可变，所以代码更安全。"),
        ]
    )
    monkeypatch.setattr(tool_evaluator, "get_agent", lambda: agent)

    outcome = tool_evaluator.evaluate_case(
        {
            "id": "tool_002",
            "question": "Python中的tuple为什么不可变？",
            "expected_tool": "knowledge_search",
        }
    )

    assert outcome.passed, outcome.failures
    assert tool_evaluator.resolve_route("Python中的tuple为什么不可变？") == "knowledge"


def test_tool_evaluator_detects_web_search(monkeypatch):
    """3. Chat route: the agent can autonomously call the web search tool."""

    messages = [
        message("请使用网页搜索功能查询今天全国主要城市的空气质量情况。"),
        message("", [{"name": "web_search", "args": {"query": "空气质量"}}]),
        message("搜索结果显示：今日北京空气质量为良。"),
    ]
    agent = FakeAgent(messages)
    monkeypatch.setattr(tool_evaluator, "get_agent", lambda: agent)

    outcome = tool_evaluator.evaluate_case(
        {
            "id": "tool_004",
            "question": "请使用网页搜索功能查询今天全国主要城市的空气质量情况。",
            "expected_tool": "web_search",
        }
    )

    assert outcome.passed, outcome.failures
    assert (
        tool_evaluator.resolve_route("请使用网页搜索功能查询今天全国主要城市的空气质量情况。")
        == "chat"
    )


def test_tool_evaluator_fails_when_expected_tool_is_missing(monkeypatch):
    """3. A chat question that never calls the expected tool fails."""

    agent = FakeAgent([message("123*456是多少？"), message("你好！")])
    monkeypatch.setattr(tool_evaluator, "get_agent", lambda: agent)

    outcome = tool_evaluator.evaluate_case(
        {
            "id": "tool_x",
            "question": "123*456是多少？",
            "expected_tool": "calculator",
        }
    )

    assert not outcome.passed
    assert 'tool "calculator" was not called' in outcome.failures


def test_tool_evaluator_flags_forbidden_tool(monkeypatch):
    """3. A tool that must not be used fails the case."""

    agent = FakeAgent(
        [
            message("你好"),
            message("", [{"name": "calculator", "args": {"expression": "1+1"}}]),
            message("你好！"),
        ]
    )
    monkeypatch.setattr(tool_evaluator, "get_agent", lambda: agent)

    outcome = tool_evaluator.evaluate_case(
        {
            "id": "tool_y",
            "question": "你好",
            "forbidden_tool": "calculator",
        }
    )

    assert not outcome.passed
    assert 'tool "calculator" should not have been called' in outcome.failures


# ------------------------------------------------------------- 4. unified runner


def test_resolve_suite_rejects_unknown_name(monkeypatch):
    """4. An unknown suite prints the usage line instead of running nothing."""

    monkeypatch.setattr(sys, "argv", ["run.py", "nope"])

    with pytest.raises(SystemExit):
        eval_run.resolve_suite(sys.argv)

    monkeypatch.setattr(sys, "argv", ["run.py"])

    with pytest.raises(SystemExit):
        eval_run.resolve_suite(sys.argv)


def test_resolve_suite_accepts_known_names(monkeypatch):
    """4. The three documented suite names are accepted."""

    for suite in SUITES:
        monkeypatch.setattr(sys, "argv", ["run.py", suite])

        assert eval_run.resolve_suite(sys.argv) == suite


def stub_run(monkeypatch: Any, outcome: EvalOutcome) -> None:
    """Patch dataset and evaluator so ``run_suite`` stays offline."""

    cases = [{"id": outcome.case_id, "question": outcome.question}]

    monkeypatch.setattr(eval_run, "load_dataset", lambda name: cases)
    monkeypatch.setattr(
        eval_run, "load_evaluator", lambda path: lambda case: outcome
    )


def test_run_suite_prints_unified_report(monkeypatch, capsys):
    """4. A passing case is rendered in the shared report format."""

    stub_run(
        monkeypatch,
        EvalOutcome(
            "rag_001",
            "Python中的tuple为什么不可变？",
            True,
            ["Keywords:\n不可变 ✓\n安全 ✓"],
            [],
        ),
    )

    passed_count, total = eval_run.run_suite("rag")
    report = capsys.readouterr().out

    assert (passed_count, total) == (1, 1)
    assert "Evaluation: rag" in report
    assert "[PASS] rag_001" in report
    assert "Question:\nPython中的tuple为什么不可变？" in report
    assert "Keywords:\n不可变 ✓\n安全 ✓" in report
    assert "Result:\n1/1 passed" in report


def test_run_suite_reports_failures(monkeypatch, capsys):
    """4. A failing case shows its reasons and is counted as a failure."""

    stub_run(
        monkeypatch,
        EvalOutcome(
            "retrieval_001",
            "Python中的变量本质是什么？",
            False,
            ["Keywords:\n变量 ✓\n引用 ✗"],
            ['keyword "引用" was not retrieved'],
        ),
    )

    passed_count, total = eval_run.run_suite("retrieval")
    report = capsys.readouterr().out

    assert (passed_count, total) == (0, 1)
    assert "[FAIL] retrieval_001" in report
    assert 'keyword "引用" was not retrieved' in report
    assert "Result:\n0/1 passed" in report


def test_run_suite_survives_evaluator_crash(monkeypatch, capsys):
    """4. An unexpected exception becomes a FAIL line, not a traceback."""

    def boom(case: dict[str, Any]) -> EvalOutcome:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        eval_run, "load_dataset", lambda name: [{"id": "x", "question": "q"}]
    )
    monkeypatch.setattr(eval_run, "load_evaluator", lambda path: boom)

    passed_count, total = eval_run.run_suite("agent")
    report = capsys.readouterr().out

    assert (passed_count, total) == (0, 1)
    assert "[FAIL] x" in report
    assert "execution error: boom" in report


if __name__ == "__main__":
    test_eval_modules_import()
    print("test_eval_modules_import: PASS")

    test_datasets_load()
    print("test_datasets_load: PASS")

    test_dataset_expectations_match_suite()
    print("test_dataset_expectations_match_suite: PASS")

    test_find_missing_keywords_is_case_insensitive()
    print("test_find_missing_keywords_is_case_insensitive: PASS")

    print("\nOffline checks passed. Use pytest for the full suite.")

