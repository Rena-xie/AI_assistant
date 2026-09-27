"""RAG chain — retrieval plus generation.

Chain under test::

    question
        -> knowledge_search()      # queries knowledge/vectorstore
        -> context string          # source + content of every chunk
        -> ChatOpenAI              # grounded generation
        -> final answer

The chain lives inside the ``aila.rag`` package (not ``aila/rag.py``)
because this package already exists and a package always shadows a
same-named module.
"""

from __future__ import annotations

from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from ..config import (
    MODEL_NAME,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
)
from ..prompts.rag_prompt import RAG_PROMPT
from ..tools.knowledge_search import knowledge_search


def build_context(question: str) -> str:
    """Retrieve knowledge base documents and turn them into a context string.

    ``knowledge_search`` already renders every retrieved document as
    ``Source: <path>`` followed by ``Content: <text>``, which is exactly
    the shape the RAG prompt expects, so no extra formatting is needed
    and the retrieval tool stays untouched.

    Args:
        question: The user question.

    Returns:
        The retrieved documents (source + content) as a single string.
    """

    return knowledge_search.invoke(question)


def create_rag_chain() -> RunnableLambda:
    """Create a retrieval-augmented generation chain.

    Returns:
        A chain that takes a ``question`` and returns the final answer.
        The result is a LangChain ``RunnableLambda``, so both
        ``chain(question)`` and ``chain.invoke(question)`` work.
    """

    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0.7
    )

    def chain(question: str) -> str:
        """Answer a question from the retrieved knowledge base content."""

        # 1. Retrieve documents from the vectorstore.
        context = build_context(question)

        # 2. Inject the retrieved context into the RAG prompt.
        messages = RAG_PROMPT.format_messages(
            context=context,
            question=question
        )

        # 3. Let the LLM generate the final answer.
        response = llm.invoke(messages)

        return response.content

    return RunnableLambda(chain)