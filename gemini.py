import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to generate embeddings using Google Gemini API
def generate_embeddings(text):
    try:
        # Load the API key from environment variables
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            raise Exception("GEMINI_API_KEY not found in environment variables")

        # Initialize the Google Gemini client with your API key
        genai.configure(api_key=API_KEY)

        # Generate embeddings using the embedContent method
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
            title="Embedding of single string"
        )

        # Return the embedding
        return result['embedding']

    except Exception as e:
        print(f"Error generating embeddings with Google Gemini: {e}")
        return None

# Function to generate responses using Google Gemini API
def generate_gemini_response(document_text, question):
    try:
        # Load the API key from environment variables
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            raise Exception("GEMINI_API_KEY not found in environment variables")
        
        # Initialize the Google Gemini client with your API key
        genai.configure(api_key=API_KEY)

        # Use the generative model for text generation (example using Gemini 1.5 Flash)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"{document_text}\n\nQuestion: {question}")

        # Return the generated response
        return response.text
    
    except Exception as e:
        print(f"Error generating response from Google Gemini: {e}")
        return f"Error generating response for '{question}'"
