
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

# Import custom modules
from helpers import extract_text_from_pdf, validate_question  # Removed generate_embeddings from helpers
from firebase import initialize_firebase, add_document, get_document_by_chat_name
from pinecone_handler import initialize_pinecone, upsert_embeddings, query_embeddings
from gemini import generate_embeddings, generate_gemini_response  # Added generate_embeddings from gemini


load_dotenv()
# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase
db = initialize_firebase()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone_index = initialize_pinecone(api_key=PINECONE_API_KEY, index="document-index")

# Define the root route to avoid 404 errors
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Document Indexing API"}), 200


# API 1: Document Upload and Indexing
@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files or 'chat_name' not in request.form:
        return jsonify({"error": "No file or chat_name provided"}), 400

    try:
        pdf_file = request.files['file']
        chat_name = request.form['chat_name']

        # Extract text and generate embeddings
        pdf_text = extract_text_from_pdf(pdf_file)
        embeddings = generate_embeddings(pdf_text)

        # Store embeddings in Pinecone
        upsert_embeddings(pinecone_index, chat_name, embeddings, {"document_text": pdf_text})

         # Store metadata in Firebase
        index_stats = pinecone_index.describe_index_stats()
        index_name = index_stats.get('name', 'unknown')
        add_document(db, chat_name, index_name)

        return jsonify({"status": "success", "message": f"Document indexed under chat name: {chat_name}"}), 200
    except Exception as e:
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
        # Retrieve document metadata from Firebase using chat_name (Pass `db`)
        doc_data = get_document_by_chat_name(db, chat_name)
        if not doc_data:
            return jsonify({"error": f"No document found for chat_name: {chat_name}"}), 404

        # Generate embeddings for the question and query Pinecone
        query_vector = generate_embeddings(question)
        pinecone_results = query_embeddings(pinecone_index, query_vector)

        # Get relevant document text and generate response from Google Gemini
        relevant_text = " ".join([match['metadata']['document_text'] for match in pinecone_results])
        gemini_response = generate_gemini_response(relevant_text, question)

        return jsonify({"status": "success", "response": gemini_response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)