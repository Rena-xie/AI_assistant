from __future__ import annotations

from langchain_core.documents import Document

from .vectorstore import load_vectorstore


def retrieve(
    query: str,
    k: int = 4,
) -> list[Document]:
    """Retrieve the most relevant knowledge chunks."""
    vectorstore = load_vectorstore()

    return vectorstore.similarity_search(
        query,
        k=k,
    )