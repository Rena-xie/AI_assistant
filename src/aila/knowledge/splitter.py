"""Document splitting utilities.

Convert large Documents into smaller chunks
for embedding and retrieval.
"""


from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    """
    Split documents into smaller chunks.

    Args:
        documents:
            List of LangChain Document objects.

    Returns:
        List of chunked Document objects.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            " ",
            ""
        ]
    )

    chunks = splitter.split_documents(
        documents
    )

    return chunks