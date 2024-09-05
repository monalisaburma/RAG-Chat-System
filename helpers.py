import PyPDF2

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def validate_question(question):
    if len(question.strip()) < 5:
        return False, "Question is too short. Please provide more details."
    return True, ""
