from __future__ import annotations

import sys

from aila.rag.retriever import retrieve


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python scripts/query_rag.py "your question"')
        raise SystemExit(1)

    query = " ".join(sys.argv[1:])

    documents = retrieve(query, k=4)

    print("=" * 60)
    print("RAG Retrieval Result")
    print("=" * 60)

    print(f"\nQuery: {query}")
    print(f"Retrieved documents: {len(documents)}")

    for index, document in enumerate(documents, start=1):
        print("\n" + "-" * 60)
        print(f"[{index}]")
        print(f"Source: {document.metadata.get('source')}")
        print()
        print(document.page_content[:1000])

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()