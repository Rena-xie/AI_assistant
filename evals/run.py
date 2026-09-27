"""Unified evaluation entry point.

Usage::

    python evals/run.py retrieval   # is the right content retrieved?
    python evals/run.py rag         # is the RAG answer grounded?
    python evals/run.py agent       # does the agent call the right tool?

The exit code is 0 when every case passed and 1 otherwise, so the command can
be used directly in CI.

The legacy scripts ``run_eval.py`` and ``run_retrieval_eval.py`` are kept and
still run against their own datasets.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ``python evals/run.py`` puts ``evals/`` on sys.path, not the project root,
# so the ``evals`` package only becomes importable after this insert.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.utils import EvalOutcome, load_dataset  # noqa: E402


EvaluateCase = Callable[[dict[str, Any]], EvalOutcome]

# suite name -> (dataset name, evaluator module)
SUITES: dict[str, tuple[str, str]] = {
    "retrieval": ("retrieval", "evals.evaluators.retrieval_evaluator"),
    "rag": ("rag", "evals.evaluators.answer_evaluator"),
    "agent": ("agent", "evals.evaluators.tool_evaluator"),
}

RULE = "=" * 28
THIN_RULE = "-" * 28


def ensure_utf8_stdout() -> None:
    """Force UTF-8 output.

    The report uses ``✓``/``✗`` marks. On Windows a redirected stdout falls
    back to the legacy code page (cp936/gbk), which cannot encode them and
    would abort the run with a ``UnicodeEncodeError``.
    """

    reconfigure = getattr(sys.stdout, "reconfigure", None)

    if reconfigure is not None:
        reconfigure(encoding="utf-8")


def load_evaluator(module_path: str) -> EvaluateCase:
    """Import one evaluator on demand.

    Suites are imported lazily so that ``run.py retrieval`` never loads the
    LLM stack that only the ``rag`` and ``agent`` suites need.

    Args:
        module_path: Dotted module path, e.g. ``evals.evaluators.tool_evaluator``.

    Returns:
        The module's ``evaluate_case`` function.
    """

    return import_module(module_path).evaluate_case


def print_case(outcome: EvalOutcome) -> None:
    """Print one case result in the shared report format.

    Args:
        outcome: Result returned by an evaluator.
    """

    verdict = "PASS" if outcome.passed else "FAIL"

    print()
    print(f"[{verdict}] {outcome.case_id}")
    print()
    print("Question:")
    print(outcome.question)

    for block in outcome.details:
        print()
        print(block)

    if outcome.failures:
        print()
        print("Failures:")

        for failure in outcome.failures:
            print(f"- {failure}")

    print()
    print(THIN_RULE)


def run_suite(name: str) -> tuple[int, int]:
    """Run every case of one suite and print the report.

    Args:
        name: Suite name, must be a key of :data:`SUITES`.

    Returns:
        ``(passed_count, total_count)``.
    """

    dataset_name, module_path = SUITES[name]
    cases = load_dataset(dataset_name)
    evaluate_case = load_evaluator(module_path)

    print(RULE)
    print(f"Evaluation: {name}")
    print(RULE)

    passed_count = 0

    for case in cases:
        try:
            outcome = evaluate_case(case)
        except Exception as exc:
            # An unexpected crash still has to show up in the report.
            outcome = EvalOutcome(
                str(case.get("id", "unknown")),
                str(case.get("question", "")),
                False,
                [],
                [f"execution error: {exc}"],
            )

        if outcome.passed:
            passed_count += 1

        print_case(outcome)

    print()
    print("Result:")
    print(f"{passed_count}/{len(cases)} passed")
    print()
    print(RULE)

    return passed_count, len(cases)


def resolve_suite(argv: list[str]) -> str:
    """Read the suite name from the command line.

    Args:
        argv: Full argument vector, ``argv[0]`` being the script path.

    Returns:
        A key of :data:`SUITES`.
    """

    names = " | ".join(SUITES)

    if len(argv) < 2 or argv[1] not in SUITES:
        raise SystemExit(f"Usage: python evals/run.py <{names}>")

    return argv[1]


def main() -> None:
    """Run the requested suite and exit non-zero when a case failed."""

    ensure_utf8_stdout()

    suite = resolve_suite(sys.argv)
    passed_count, total = run_suite(suite)

    if passed_count != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
