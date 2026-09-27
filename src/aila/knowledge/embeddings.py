"""Embedding model factory."""

from langchain_community.embeddings import DashScopeEmbeddings

from ..config import DASHSCOPE_API_KEY


def create_embeddings():
    """
    Create embedding model.

    Returns:
        DashScope embedding model.
    """

    embeddings = DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=DASHSCOPE_API_KEY
    )

    return embeddings