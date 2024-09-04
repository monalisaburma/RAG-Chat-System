# helpers.py
import PyPDF2

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def validate_question(question):
    if len(question.strip()) < 5:
        return False, "Question is too short. Please provide more details."
    return True, ""
