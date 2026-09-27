"""Knowledge document loader.

Load markdown documents from the knowledge source directory
and convert them into LangChain Document objects.
"""


from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Single knowledge source: every raw markdown document lives here.
# Sub-directories (official/, learning_notes/, ...) are scanned
# recursively, so adding a new document folder needs no code change.
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge" / "documents"


def load_markdown_documents() -> list[Document]:
    """
    Load all markdown files from the knowledge source directory.

    KNOWLEDGE_DIR is scanned recursively; a missing directory is
    skipped instead of raising an error.

    Returns:
        List of LangChain Document objects.
    """

    documents = []


    if not KNOWLEDGE_DIR.exists():
        return documents


    # sorted() keeps the load order stable between rebuilds.
    for file_path in sorted(KNOWLEDGE_DIR.rglob("*.md")):

        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )

        docs = loader.load()


        for doc in docs:

            # Keep the real path relative to the project root,
            # e.g. "knowledge/documents/learning_notes/数据类型与变量.md".
            # as_posix() stores forward slashes on every platform.
            doc.metadata["source"] = (
                file_path
                .relative_to(PROJECT_ROOT)
                .as_posix()
            )

            documents.append(doc)


    return documents