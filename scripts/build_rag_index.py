from pathlib import Path

from aila.rag.loader import (
    load_markdown_documents,
    split_documents,
)
from aila.rag.vectorstore import build_vectorstore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


def main() -> None:
    print("=" * 60)
    print("Building RAG Knowledge Index")
    print("=" * 60)

    print(f"\nKnowledge directory:")
    print(KNOWLEDGE_DIR)

    documents = load_markdown_documents(KNOWLEDGE_DIR)

    print(f"\nLoaded documents: {len(documents)}")

    chunks = split_documents(documents)

    print(f"Generated chunks: {len(chunks)}")

    build_vectorstore(chunks)

    print("\nVector store built successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()