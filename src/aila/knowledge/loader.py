"""Knowledge document loader.

Load markdown documents from knowledge directory
and convert them into LangChain Document objects.
"""


from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


PROJECT_ROOT = Path(__file__).resolve().parents[3]

KNOWLEDGE_DIR = (
    PROJECT_ROOT
    / "knowledge"
    / "official"
)


def load_markdown_documents() -> list[Document]:
    """
    Load all markdown files from knowledge directory.

    Returns:
        List of LangChain Document objects.
    """

    documents = []


    for file_path in KNOWLEDGE_DIR.rglob("*.md"):

        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )

        docs = loader.load()


        for doc in docs:

            doc.metadata["source"] = str(
                file_path.relative_to(PROJECT_ROOT)
            )

            documents.append(doc)


    return documents