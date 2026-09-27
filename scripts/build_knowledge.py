from aila.knowledge.loader import load_markdown_documents
from aila.knowledge.splitter import split_documents
from aila.knowledge.vectorstore import create_vectorstore


def main():

    print("Loading documents...")

    docs = load_markdown_documents()

    print("documents:", len(docs))


    print("Splitting...")

    chunks = split_documents(docs)

    print("chunks:", len(chunks))


    print("Building vectorstore...")

    create_vectorstore(chunks)

    print("Done.")


if __name__ == "__main__":
    main()