"""Evaluators — one module per layer of the stack.

Each module exposes the same entry point so ``evals/run.py`` can dispatch by
name:

    evaluate_case(case: dict) -> EvalOutcome

* :mod:`retrieval_evaluator` — is the right content retrieved?
* :mod:`answer_evaluator`    — is the RAG answer grounded in the knowledge base?
* :mod:`tool_evaluator`      — does the agent call the right tool?
"""
