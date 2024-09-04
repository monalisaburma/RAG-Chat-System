import pinecone

# Initialize Pinecone
pinecone.init(api_key="your_pinecone_api_key", environment="your_pinecone_environment")

# Create an index
pinecone.create_index("document-index", dimension=512)  # '512' depends on the embedding model
index = pinecone.Index("document-index")
