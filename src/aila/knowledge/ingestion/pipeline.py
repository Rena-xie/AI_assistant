"""Ingestion pipeline: load -> clean -> split -> embed -> store.

Builds the knowledge base from raw files in ``knowledge/documents/`` and
persists it to ``knowledge/vectorstore/`` — the same store that the
``knowledge_search`` tool reads. It reuses the existing embedding/splitter/
vectorstore helpers under ``aila.knowledge``, so the RAG architecture stays
untouched.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

from .cleaner import clean_documents
from .loader import default_knowledge_dir, load_documents
from ..splitter import split_documents
from ..vectorstore import create_vectorstore


def build_chunks(directory: Path | None = None) -> list[Document]:
    """Run load -> clean -> split and return the resulting chunks.

    This half of the pipeline is pure and offline, so it can be unit-tested
    without an embedding API key.
    """

    directory = directory if directory is not None else default_knowledge_dir()

    documents = load_documents(directory)
    documents = clean_documents(documents)
    chunks = split_documents(documents)

    return chunks


def build_knowledge_base(directory: Path | None = None) -> int:
    """Build the full knowledge base and return the number of stored chunks.

    Runs load -> clean -> split -> embed -> store. Embedding and storage are
    delegated to ``aila.knowledge.embeddings`` / ``aila.knowledge.vectorstore``.
    """

    chunks = build_chunks(directory)

    create_vectorstore(chunks)

    return len(chunks)
