"""Unit tests for the question router."""

from aila.graph.router import route_question


def test_knowledge_question():
    state = {
        "messages": [
            {"role": "user", "content": "LangGraph中的StateGraph是什么？"}
        ]
    }
    result = route_question(state)
    assert result == "knowledge", f"Expected 'knowledge', got '{result}'"


def test_chat_question():
    state = {
        "messages": [
            {"role": "user", "content": "今天天气怎么样？"}
        ]
    }
    result = route_question(state)
    assert result == "chat", f"Expected 'chat', got '{result}'"


if __name__ == "__main__":
    test_knowledge_question()
    print("test_knowledge_question: PASS")

    test_chat_question()
    print("test_chat_question: PASS")

    print("\nAll tests passed.")
