from pathlib import Path
import shutil

from langchain_chroma import Chroma

from .embeddings import create_embeddings


VECTORSTORE_PATH = Path("knowledge/vectorstore")


def create_vectorstore(chunks):
    """Create a Chroma vectorstore from chunks, removing any existing data first.

    If ``VECTORSTORE_PATH`` already exists, it is recursively deleted before
    a fresh vectorstore is built. This ensures a clean rebuild rather than
    accumulating duplicate documents.

    Returns:
        Chroma: The newly created vectorstore, persisted to ``VECTORSTORE_PATH``.
    """
    embeddings = create_embeddings()

    # Rebuild semantics: drop the previous local store right before writing,
    # so a failed embed step does not destroy an existing knowledge base.
    if VECTORSTORE_PATH.exists():
        shutil.rmtree(VECTORSTORE_PATH)
    VECTORSTORE_PATH.parent.mkdir(parents=True, exist_ok=True)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTORSTORE_PATH)
    )

    return vectorstore