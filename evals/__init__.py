"""Evaluation framework for the AI Learning Assistant.

Layout::

    run.py                      unified CLI entry point
    datasets/<suite>.json       evaluation cases, one file per suite
    evaluators/<layer>.py       one evaluator per layer under test
    utils/                      shared loading + reporting helpers

Every suite targets one layer of the stack, so a failure points at exactly
one component::

    retrieval -> knowledge_search            (vectorstore only, no LLM)
    rag       -> create_rag_chain            (retrieval + grounded answer)
    agent     -> create_agent                (routing + tool calling)

Run a suite with::

    python evals/run.py retrieval
    python evals/run.py rag
    python evals/run.py agent

The legacy scripts ``run_eval.py`` and ``run_retrieval_eval.py`` are kept
unchanged and still work against their own datasets.
"""
