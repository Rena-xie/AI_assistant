from langchain_core.tools import tool
from langchain_chroma import Chroma

from ..knowledge.embeddings import create_embeddings


VECTORSTORE_PATH = "knowledge/vectorstore"


@tool
def knowledge_search(query: str) -> str:
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
        Relevant document contents.
    """

    embeddings = create_embeddings()

    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k":3
        }
    )

    docs = retriever.invoke(query)

    if not docs:
        return "No relevant documents found."

    results=[]

    for doc in docs:
        results.append(
            f"""
Source:
{doc.metadata.get('source')}

Content:
{doc.page_content}
"""
        )

    return "\n\n".join(results)