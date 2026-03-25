import os
import json
import pdfplumber
import fitz # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any


class FileManager:
    @staticmethod
    def extract_info(folder_path: Path) -> List[Dict[str, Any]]:
        info_list = []

        for file_path in folder_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                json_file_name = file_path.name
                dir_name = file_path.stem
                data = json.load(f)
                info_list.append({
                    "dir_name": dir_name,
                    "json_file_name": json_file_name,
                    "data": data
                })
                
        return info_list

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