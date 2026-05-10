import PyPDF2
import docx

def extract_text_from_file(file):

    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return " ".join([p.extract_text() or "" for p in reader.pages])

    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return " ".join([p.text for p in doc.paragraphs])

    return ""