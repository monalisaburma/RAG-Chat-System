import streamlit as st
import requests

# Streamlit app
st.title("RAG-based Chat System")

# Streamlit for file upload and user interaction
st.header("Upload a PDF Document")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
chat_name = st.text_input("Enter a unique chat name for this document")

if uploaded_file and chat_name:
    if st.button("Upload Document"):
        files = {"file": uploaded_file.getvalue()}
        data = {"chat_name": chat_name}
        
        response = requests.post("http://127.0.0.1:5000/upload", files=files, data=data)
        
        if response.status_code == 200:
            st.success(f"Document indexed under chat name: {chat_name}")
        else:
            st.error(f"Error: {response.json().get('error')}")

# Streamlit for querying the document
st.header("Query the Document")
query_chat_name = st.text_input("Enter the chat name to query")
question = st.text_input("Enter your question")

if query_chat_name and question:
    if st.button("Submit Query"):
        data = {"chat_name": query_chat_name, "question": question}
        response = requests.post("http://127.0.0.1:5000/query_document", data=data)
        
        if response.status_code == 200:
            st.success(f"Response: {response.json().get('response')}")
        else:
            st.error(f"Error: {response.json().get('error')}")

