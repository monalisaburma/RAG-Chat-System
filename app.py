from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Import custom modules
from helpers import extract_text_from_pdf, validate_question
from firebase import initialize_firebase, add_document, get_document_by_chat_name
from pinecone_handler import initialize_pinecone, upsert_embeddings, query_embeddings
from gemini import generate_embeddings, generate_gemini_response

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit for file uploads

# Initialize Firebase
db = initialize_firebase()

# Initialize Pinecone with API key from environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone_index = initialize_pinecone(api_key=PINECONE_API_KEY, index_name="document-index")


# API 1: Document Upload and Indexing
@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files or 'chat_name' not in request.form:
        return jsonify({"error": "No file or chat_name provided"}), 400

    try:
        pdf_file = request.files['file']
        chat_name = request.form['chat_name']

        # Extract text from the uploaded PDF
        pdf_text = extract_text_from_pdf(pdf_file)

        # Generate embeddings from the PDF text
        embeddings = generate_embeddings(pdf_text)

        # Upsert the embeddings into Pinecone (connects to 'document-index')
        upsert_embeddings(pinecone_index, chat_name, embeddings, {"document_text": pdf_text})

        # Use the correct Pinecone index name
        pinecone_index_name = "document-index"  # This should match the index name used in Pinecone
        print(f"Using Pinecone Index: {pinecone_index_name}")  # Debugging line to ensure pinecone_index is correct

        # Pass the db instance, chat_name, and pinecone index name to add_document
        add_document(db, chat_name, pinecone_index_name)

        return jsonify({"status": "success", "message": f"Document indexed under chat name: {chat_name}"}), 200
    except Exception as e:
        print(f"Error during document upload: {e}")  # Debugging line to track the error message
        return jsonify({"error": str(e)}), 500



# API 2: Document Querying and Guardrails
@app.route('/query_document', methods=['POST'])
def query_document():
    if 'chat_name' not in request.form or 'question' not in request.form:
        return jsonify({"error": "Both chat_name and question are required."}), 400

    chat_name = request.form['chat_name']
    question = request.form['question']

    # Validate the question (Guardrails)
    is_valid, error_message = validate_question(question)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    try:
        # Retrieve document metadata from Firebase using chat_name
        doc_data = get_document_by_chat_name(db, chat_name)
        if not doc_data:
            return jsonify({"error": f"No document found for chat_name: {chat_name}"}), 404

        # Generate embeddings for the question and query Pinecone for relevant sections
        query_vector = generate_embeddings(question)
        if not query_vector:
            return jsonify({"error": "Failed to generate embeddings for the question."}), 500

        pinecone_results = query_embeddings(pinecone_index, query_vector)
        if not pinecone_results or 'matches' not in pinecone_results:
            return jsonify({"error": "No relevant matches found."}), 404

        # Get relevant document text and generate a response from Google Gemini
        relevant_text = " ".join([match['metadata']['document_text'] for match in pinecone_results['matches']])
        gemini_response = generate_gemini_response(relevant_text, question)

        return jsonify({"status": "success", "response": gemini_response}), 200
    except Exception as e:
        print(f"Error querying document: {e}")
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
