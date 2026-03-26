import pdfplumber
import fitz # PyMuPDF
from pathlib import Path

class PdfExtractor:
    @staticmethod
    def extract_text_from_pdf(pdf_path: Path) -> str:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

            if not text.strip():
                # Fallback para PyMuPDF se pdfplumber não extrair texto
                doc = fitz.open(pdf_path)
                text = "\n".join(page.get_text() for page in doc)
                doc.close()

            return text
        except Exception as e:
            print(f"Erro ao extrair texto do PDF '{pdf_path}': {e}")
            return ""