"""Tests for short-term conversation memory across LangGraph threads."""

from langgraph.checkpoint.memory import MemorySaver

from aila.agent import create_agent
from aila.memory import create_checkpointer
from aila.runtime.runner import run_agent


def _message_text(message):
    if hasattr(message, "content"):
        return message.content
    if isinstance(message, dict):
        return message.get("content", "")
    return str(message)


def test_create_checkpointer_returns_memory_saver():
    """The memory module exposes the official LangGraph checkpointer."""
    checkpointer = create_checkpointer()
    assert isinstance(checkpointer, MemorySaver)


def test_same_thread_remembers_previous_turn():
    """The same thread_id should preserve the prior conversation state."""
    agent = create_agent()

    run_agent(agent, "我正在学习 AI 应用开发。", thread_id="memory_same_thread")
    second = run_agent(agent, "我正在学习什么？", thread_id="memory_same_thread")

    answer = _message_text(second)
    assert "AI 应用开发" in answer or "AI应用开发" in answer, answer


def test_different_threads_are_isolated():
    """Different thread_id values should not share the same conversation state."""
    agent = create_agent()

    run_agent(agent, "我叫张三。", thread_id="thread_a")
    answer_a = run_agent(agent, "我叫什么？", thread_id="thread_a")
    answer_b = run_agent(agent, "我叫什么？", thread_id="thread_b")

    a_text = _message_text(answer_a)
    b_text = _message_text(answer_b)

    assert "张三" in a_text, a_text
    assert "张三" not in b_text, b_text


if __name__ == "__main__":
    test_create_checkpointer_returns_memory_saver()
    test_same_thread_remembers_previous_turn()
    test_different_threads_are_isolated()
    print("All memory tests passed.")
