from langchain_chroma import Chroma

from aila.knowledge.embeddings import create_embeddings


def main():

    vectorstore = Chroma(
        persist_directory="knowledge/vectorstore",
        embedding_function=create_embeddings()
    )


    query = "LangGraph中的StateGraph是什么？"


    results = vectorstore.similarity_search(
        query,
        k=3
    )


    print("Query:")
    print(query)


    print("\nRetrieved documents:")


    for i, doc in enumerate(results):

        print("\n" + "=" * 50)

        print("Rank:", i + 1)

        print(
            "Source:",
            doc.metadata["source"]
        )

        print(
            doc.page_content[:500]
        )


if __name__ == "__main__":
    main()