import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

def initialize_pinecone(api_key, index_name):
    api_key = os.getenv("PINECONE_API_KEY")  # Ensure your .env has the correct Pinecone API key
    pc = Pinecone(api_key=api_key)  # Initialize Pinecone with your API key
    index = pc.Index(index_name)  # Use the index you already created in the Pinecone dashboard
    return index

def upsert_embeddings(index, chat_name, embeddings, metadata):
    try:
        index.upsert(
            vectors=[{
                "id": chat_name,
                "values": embeddings,
                "metadata": metadata
            }],
            namespace="documents"
        )
    except Exception as e:
        print(f"Error during upsert: {e}")

def query_embeddings(index, query_vector):
    try:
        print(f"Querying embeddings for vector: {query_vector}")
        result = index.query(
            namespace="documents",
            vector=query_vector,
            top_k=2,
            include_metadata=True
        )
        print(f"Query results: {result}")
        return result
    except Exception as e:
        print(f"Error during Pinecone query: {e}")
        return None
