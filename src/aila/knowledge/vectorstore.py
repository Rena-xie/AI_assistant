from pathlib import Path

from langchain_chroma import Chroma

from .embeddings import create_embeddings


VECTORSTORE_PATH = Path("knowledge/vectorstore")


def create_vectorstore(chunks):

    embeddings = create_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTORSTORE_PATH)
    )

    return vectorstore