from pathlib import Path
from typing import Tuple, List

from src.utils.logging_utils import LoggingService
from src.utils.file_utils import FileManager

from src.extractor.config import Config
from src.extractor.pdf_extractor import PdfExtractor
from src.extractor.docx_extractor import DocxExtractor
from src.extractor.spreadsheet_extractor import SpreadsheetExtractor
from src.extractor.zip_extractor import ZipExtractor
from src.extractor.doc_extractor import DocExtractor
from src.extractor.odt_extractor import OdtExtractor


logger = LoggingService.get_logger("extractor.attachment")

class AttachmentReader:
    """Classe responsável por ler e extrair texto dos anexos de uma licitação."""

    @staticmethod
    def read_attachment(folder_path: Path, processed_files: List[str] = None, full_text: str = "") -> Tuple[str, List[str]]:
        """
        Extrai e concatena texto de todos os anexos relevantes de uma licitação.
        Retorna (texto_completo, lista_de_arquivos_processados).
        """
        if not folder_path.exists() or not folder_path.is_dir():
            logger.info(f"Pasta de anexos não encontrada: {folder_path}")
            return "", []

        if not processed_files:
            processed_files = []

        if not full_text:
            full_text = ""

        for file_path in folder_path.iterdir():
            file_ext = FileManager.get_file_extension(file_path)
            if file_ext in Config.SUPPORTED_FILE_TYPES:
                match file_ext:
                    case ".pdf":
                        text = PdfExtractor.extract_text_from_pdf(file_path)
                        full_text += f"\n\n--- Texto extraído de {file_path.name} ---\n{text}"
                        processed_files.append(file_path.name)
                    case ".docx":
                        text = DocxExtractor.extract_text_from_docx(file_path)
                        full_text += f"\n\n--- Texto extraído de {file_path.name} ---\n{text}"
                        processed_files.append(file_path.name)
                    case ".doc":
                        text = DocExtractor.extract_text_from_doc(file_path)
                        full_text += f"\n\n--- Texto extraído de {file_path.name} ---\n{text}"
                        processed_files.append(file_path.name)
                    case ".odt":
                        text = OdtExtractor.extract_text_from_odt(file_path)
                        full_text += f"\n\n--- Texto extraído de {file_path.name} ---\n{text}"
                        processed_files.append(file_path.name)
                    case ".xls" | ".xlsx" | ".ods":
                        text = SpreadsheetExtractor.extract_text_from_spreadsheet(file_path, file_extension=file_ext)
                        full_text += f"\n\n--- Texto extraído de {file_path.name} ---\n{text}"
                        processed_files.append(file_path.name)
                    case ".zip":
                        file_name = FileManager.get_file_name(file_path)
                        extract_folder = folder_path / file_name
                        ZipExtractor.extract_zip_file(file_path, extract_folder)
                        full_text, processed_files = AttachmentReader.read_attachment(extract_folder, processed_files, full_text)
            else:
                logger.warning(f"Tipo de arquivo não suportado ({file_ext}): {file_path.name}")

        if not processed_files:
            logger.warning(f"Nenhum arquivo de anexo processado na pasta: {folder_path}")

        return full_text, processed_files