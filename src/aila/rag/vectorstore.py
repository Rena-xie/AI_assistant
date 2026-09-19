from __future__ import annotations

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from .embeddings import create_embeddings


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VECTORSTORE_DIR = PROJECT_ROOT / "storage" / "chroma"

COLLECTION_NAME = "aila_knowledge"


def build_vectorstore(
    documents: list[Document],
) -> Chroma:
    """
    Rebuild the local Chroma vector store from documents.
    """
    VECTORSTORE_DIR.parent.mkdir(parents=True, exist_ok=True)

    if VECTORSTORE_DIR.exists():
        shutil.rmtree(VECTORSTORE_DIR)

    embeddings = create_embeddings()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTORSTORE_DIR),
    )

    return vectorstore


def load_vectorstore() -> Chroma:
    """Load the existing local Chroma vector store."""
    if not VECTORSTORE_DIR.exists():
        raise FileNotFoundError(
            f"Vector store does not exist: {VECTORSTORE_DIR}\n"
            "Run build_rag_index.py first."
        )

    embeddings = create_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )