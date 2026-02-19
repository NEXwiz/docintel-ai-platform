from pypdf import PdfReader
from docx import Document
import os

def extract_text(file_path:str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_pdf_text(file_path)
    elif ext == ".docx":
        return extract_docx_text(file_path)
    elif ext == ".txt":
        return extract_txt_file(file_path)
    else:
        return ValueError("Unsupported file format")
    
def extract_pdf_text(path:str) -> str:
    reader = PdfReader(path)
    text = []
    for page in reader.pages:
        if page.extract_text():
            text.append(page.extract_text())
    return "\n".join(text)

def extract_docx_text(path:str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_txt_file(path:str) -> str:
    with open(path, "r",encoding="utf-8",errors="ignore") as f:
        return f.read()
