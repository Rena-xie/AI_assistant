"""Rebuild the knowledge base through the ingestion pipeline.

Kept as a thin wrapper so the documented command keeps working::

    python scripts/build_knowledge.py

The pipeline runs load -> clean -> split -> embed -> store against
``knowledge/documents/`` and persists to ``knowledge/vectorstore/``.
"""

from aila.knowledge.ingestion.pipeline import build_knowledge_base


def main() -> None:
    print("Building knowledge base (load -> clean -> split -> embed -> store)...")

    chunk_count = build_knowledge_base()

    print(f"chunks: {chunk_count}")
    print("Done.")


if __name__ == "__main__":
    main()
