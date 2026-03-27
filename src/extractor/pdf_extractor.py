import pdfplumber
import fitz # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path
from src.utils.logging_utils import LoggingService

logger = LoggingService.get_logger("extractor.pdf")

class PdfExtractor:
    """Classe responsável por extrair texto de arquivos PDF, utilizando pdfplumber como método principal e PyMuPDF como fallback."""
    @staticmethod
    def extract_text_from_pdf(pdf_path: Path) -> str:
        """Extrai texto de um arquivo PDF. Retorna o texto extraído ou uma string vazia em caso de falha."""
        if not pdf_path.exists() or not pdf_path.is_file():
            logger.warning(f"Arquivo PDF não encontrado: {pdf_path}")
            return ""

        if pdf_path.stat().st_size == 0:
            logger.warning(f"Arquivo vazio (0 bytes) ignorado: {pdf_path.name}")
            return ""

        logger.info(f"Começando extração de arquivo PDF: {pdf_path}")
        
        is_pdf_broken = False

        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

                if text.strip():
                    logger.info("Texto extraído com sucesso do arquivo PDF (utilizando pdfplumber)")
                    return text

        except Exception as e:
            logger.warning(f"Erro ao ler PDF (pdfplumber) '{pdf_path}': {e}")
            is_pdf_broken = True

        # Fallback para PyMuPDF se pdfplumber não extrair texto
        try:
            doc = fitz.open(pdf_path)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()

            if text.strip():
                logger.info("Texto extraído com sucesso do arquivo PDF (utilizando PyMuPDF)")
                return text

        except fitz.FileDataError as e:
            logger.error(f"Arquivo não é um PDF válido ou está totalmente corrompido '{pdf_path.name}': {e}")
            return ""

        except Exception as e:
            logger.error(f"Falha total ao extrair '{pdf_path.name}' após 2 tentativas: {e}")
            return ""

        if is_pdf_broken:
            logger.warning(f"PDF '{pdf_path.name}' pode estar corrompido ou protegido, abortando tentativa de OCR.")
            return ""

        # Fallback para OCR se o PyMuPDF não extrair texto
        try:
            images = convert_from_path(pdf_path)
            ocr_text = []

            for image in images:
                image_text = pytesseract.image_to_string(image, lang='por')
                ocr_text.append(image_text)

            full_ocr_text = "\n".join(ocr_text).strip()
            if full_ocr_text:
                logger.info(f"Texto extraído com sucesso utilizando OCR (Tesseract)!")
                return full_ocr_text

            logger.warning(f"Nenhum texto extraído do arquivo PDF, mesmo utilizando OCR!")
            return ""

        except Exception as e:
            logger.warning(f"Erro ao extrair texto de PDF utilizando OCR: {e}")
            return ""