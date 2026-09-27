"""Tests for the RAG chain: retrieval plus grounded generation."""

from aila.rag import build_context, create_rag_chain


QUESTION = "Python中的变量本质是什么？"


def test_rag_chain_retrieves_context():
    """1 + 2. The chain can query the vectorstore and build a context."""

    context = build_context(QUESTION)

    print("=== Context ===")
    print(context)
    print("===============")

    # 1. 能调用 vectorstore（检索到内容）
    assert context.strip(), "Context should not be empty"

    # 检索结果必须带上文档来源，才能作为 RAG 的 context 使用
    assert "Source:" in context, "Context should carry document sources"

    assert "Content:" in context, "Context should carry document content"


def test_rag_chain_answer_is_grounded():
    """3. The final answer is generated from the retrieved knowledge base."""

    chain = create_rag_chain()
    answer = chain.invoke(QUESTION)

    print("=== Answer ===")
    print(answer)
    print("==============")

    assert answer.strip(), "Answer should not be empty"

    # 学习笔记里把变量解释为"指向内存中对象的指针/标记"，
    # 所以回答里应出现"变量"或"引用"。
    assert "变量" in answer or "引用" in answer, (
        "Answer should mention '变量' or '引用'"
    )


if __name__ == "__main__":
    test_rag_chain_retrieves_context()
    print("test_rag_chain_retrieves_context: PASS")

    test_rag_chain_answer_is_grounded()
    print("test_rag_chain_answer_is_grounded: PASS")

    print("\nAll tests passed.")