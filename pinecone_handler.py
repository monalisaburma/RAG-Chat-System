import os
from dotenv import load_dotenv
from pinecone import Pinecone
load_dotenv()

def initialize_pinecone(api_key, index):
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    index = pc.Index("document-index")
    return index

def upsert_embeddings(index, chat_name, embeddings, metadata):
    index.upsert(
        vectors=[{
            "id": chat_name,
            "values": embeddings,
            "metadata": metadata
        }],
        namespace="documents"
    )

def query_embeddings(index, query_vector):
    return index.query(
        namespace="documents",
        vector=query_vector,
        top_k=2,
        include_metadata=True
    )
