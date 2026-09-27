"""Tests for the retrieval layer.

Covers the vectorstore and the ``knowledge_search`` tool without
invoking the agent.
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document

from aila.knowledge.embeddings import create_embeddings
from aila.tools.knowledge_search import VECTORSTORE_PATH, knowledge_search


QUERY = "Python中的变量本质是什么？"


def load_vectorstore() -> Chroma:
    """Open the persisted Chroma vectorstore (read-only)."""
    return Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=create_embeddings(),
    )


def test_vectorstore_loads():
    """1. The vectorstore can be loaded and is not empty."""
    vectorstore = load_vectorstore()

    data = vectorstore.get()

    assert data["ids"], "Vectorstore should contain at least one chunk"


def test_knowledge_search_returns_documents():
    """2. Retrieval returns Document objects and a non-empty tool result."""
    vectorstore = load_vectorstore()

    docs = vectorstore.similarity_search(QUERY, k=3)

    assert docs, "similarity_search should return at least one document"

    for doc in docs:
        assert isinstance(doc, Document), "retrieved items must be Document"

    result = knowledge_search.invoke(QUERY)

    assert isinstance(result, str), "knowledge_search must return a string"
    assert result.strip(), "knowledge_search must not return an empty string"


def test_retrieved_metadata_contains_source():
    """3. Every retrieved document carries a non-empty ``source``."""
    vectorstore = load_vectorstore()

    docs = vectorstore.similarity_search(QUERY, k=3)

    assert docs, "similarity_search should return at least one document"

    for doc in docs:
        assert "source" in doc.metadata, "metadata must contain 'source'"
        assert doc.metadata["source"], "'source' must not be empty"


if __name__ == "__main__":
    test_vectorstore_loads()
    print("test_vectorstore_loads: PASS")

    test_knowledge_search_returns_documents()
    print("test_knowledge_search_returns_documents: PASS")

    test_retrieved_metadata_contains_source()
    print("test_retrieved_metadata_contains_source: PASS")

    print("\nAll tests passed.")