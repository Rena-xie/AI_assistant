"""Tests for LangSmith tracing observability setup.

This project does not require live LangSmith uploads for local development.
The goal is to ensure the project loads cleanly and that tracing settings are
optional rather than breaking local execution.
"""

import os

import pytest

from aila.agent import create_agent


def test_project_imports_and_agent_can_be_created():
    """The package and graph factory still import and construct normally."""
    assert create_agent is not None
    agent = create_agent()
    assert agent is not None


def test_langsmith_api_key_is_optional_for_local_runs(monkeypatch):
    """Without a LangSmith API key, local execution should still work."""
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")

    assert os.getenv("LANGCHAIN_TRACING_V2") == "true"
    assert os.getenv("LANGCHAIN_API_KEY") is None

    agent = create_agent()
    assert agent is not None


if __name__ == "__main__":
    test_project_imports_and_agent_can_be_created()
    print("test_project_imports_and_agent_can_be_created: PASS")

    # Direct-run equivalent of the monkeypatch-based test: no API key,
    # tracing flag on, agent must still be created locally.
    os.environ.pop("LANGCHAIN_API_KEY", None)
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    assert create_agent() is not None
    print("test_langsmith_api_key_is_optional_for_local_runs: PASS")

    print("All observability tests passed.")
