# firebase.py

import firebase_admin
from firebase_admin import credentials, firestore
import os

def initialize_firebase():
    cred_path = os.path.join('config', 'rag-chat-api-firebase-adminsdk-1svn8-68d8aca0bf.json')  # Update the path if necessary
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

def add_document(db, chat_name, pinecone_index):
    doc_ref = db.collection('documents').add({
        'chat_name': chat_name,
        'pinecone_index': pinecone_index
    })
    return doc_ref

def get_document_by_chat_name(db, chat_name):
    docs = db.collection('documents').where('chat_name', '==', chat_name).stream()
    doc_data = None
    for doc in docs:
        doc_data = doc.to_dict()
        break
    return doc_data
