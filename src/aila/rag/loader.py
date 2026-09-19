from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_markdown_documents(
    knowledge_dir: Path,
) -> list[Document]:
    """Load all Markdown files under the knowledge directory."""
    documents: list[Document] = []

    for path in sorted(knowledge_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")

        if not text.strip():
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(path.relative_to(knowledge_dir)),
                    "file_path": str(path),
                },
            )
        )

    return documents


def split_documents(
    documents: list[Document],
) -> list[Document]:
    """Split documents into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
    )

    return splitter.split_documents(documents)