import chromadb

client = chromadb.Client()

collection = client.create_collection("knowledge")

collection.add(
    documents=[
        "Python is a programming language known for simplicity.",
        "Chromadb is a vector database for storing and searching documents.",
        "RAG stands for Retrieval-Augmented Generation. It fetches relevant documents before answering.",
        "An AI agent can think, act and use tools to complete tasks.",
        "Lanchain is a framework for building AI agents that can use tools and access external data."
    ],
    ids=["doc1", "doc2", "doc3", "doc4", "doc5"]
)

results = collection.query(
    query_texts=["What is Python?"],
    n_results=2
)

print(results['documents'])