"""Test knowledge_search tool directly."""

from aila.tools.knowledge_search import knowledge_search


def test_rag_tool():

    result = knowledge_search.invoke(
        "LangGraph中的StateGraph是什么？"
    )

    print("=== Result ===")
    print(result)
    print("==============")

    # 1. 返回结果非空
    assert result, "Result should not be empty"

    # 2. 包含 langgraph 或 StateGraph
    lower = result.lower()
    assert "langgraph" in lower or "stategraph" in lower, (
        "Result should contain 'langgraph' or 'StateGraph'"
    )


if __name__ == "__main__":
    test_rag_tool()
    print("All tests passed.")