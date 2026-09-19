from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


def create_embeddings() -> DashScopeEmbeddings:
    """Create the embedding model used by the knowledge base."""
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "DASHSCOPE_API_KEY is not configured in the project .env file."
        )

    model = os.getenv(
        "EMBEDDING_MODEL",
        "text-embedding-v4",
    )

    return DashScopeEmbeddings(
        model=model,
        dashscope_api_key=api_key,
    )