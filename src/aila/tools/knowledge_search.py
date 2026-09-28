from langchain_core.tools import tool
from langchain_chroma import Chroma

from ..knowledge.embeddings import create_embeddings


VECTORSTORE_PATH = "knowledge/vectorstore"


@tool
def knowledge_search(query: str):
    """
    Search AI knowledge documents.

    Use this tool when the user asks about:
    - LangGraph
    - LangChain
    - RAG
    - Agent architecture
    - AI application development

    Args:
        query:
            User question.

    Returns:
        Relevant document contents and exact source metadata from the
        underlying LangChain Document objects.
    """

    embeddings = create_embeddings()

    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 3
        }
    )

    docs = retriever.invoke(query)

    if not docs:
        return {"context": "No relevant documents found.", "sources": []}

    context_parts = []
    source_map = {}

    for doc in docs:
        metadata = doc.metadata or {}
        source_value = metadata.get("source")

        if source_value:
            source_key = str(source_value)
            if source_key not in source_map:
                source_entry = {"source": str(source_value)}
                if metadata.get("page") is not None:
                    source_entry["page"] = metadata["page"]
                if metadata.get("title") is not None:
                    source_entry["title"] = str(metadata["title"])
                source_map[source_key] = source_entry

            context_parts.append(
                f"""
Source:
{source_value}

Content:
{doc.page_content}
"""
            )
        else:
            context_parts.append(doc.page_content)

    return {
        "context": "\n\n".join(context_parts),
        "sources": list(source_map.values()),
    }