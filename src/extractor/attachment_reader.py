from pathlib import Path
from typing import Tuple, List, Optional

from src.utils.logging_utils import LoggingService
from src.utils.file_utils import FileManager

from src.extractor.config import Config
from src.extractor.pdf_extractor import PdfExtractor
from src.extractor.docx_extractor import DocxExtractor
from src.extractor.spreadsheet_extractor import SpreadsheetExtractor
from src.extractor.zip_extractor import ZipExtractor
from src.extractor.doc_extractor import DocExtractor
from src.extractor.odt_extractor import OdtExtractor
from src.parser.text_parser import TextParser

logger = LoggingService.get_logger("extractor.attachment")

class AttachmentReader:
    """Classe responsável por ler e extrair texto dos anexos de uma licitação."""

    @staticmethod
    def read_attachment(folder_path: Path, processed_files: Optional[List[str] | None] = None, full_text: str = "") -> Tuple[str, List[str]]:
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
            if file_path.is_dir():
                continue
                
            if not FileManager.verify_file_exists(file_path):
                logger.warning(f"Arquivo de anexo não encontrado: {file_path.name}")
                continue

            file_ext = FileManager.get_file_extension(file_path)

            if not file_ext or file_ext not in Config.SUPPORTED_FILE_TYPES:
                guess_extension = FileManager.guess_file_extension(file_path)

                if guess_extension in Config.SUPPORTED_FILE_TYPES:
                    logger.info(f"Extensão do arquivo '{file_path.name}' corrigida para '{file_ext}' com base na análise de conteúdo.")

                    file_ext = guess_extension
                    new_file_path = file_path.with_name(f"{file_path.name}{file_ext}")
                    file_path.rename(new_file_path)
                    file_path = new_file_path
                else:
                    logger.warning(f"Extensão do arquivo ({file_ext if file_ext else guess_extension}) '{file_path.name}' não encontrada ou arquivo não suportado!")
                    continue
            
            match file_ext:
                case ".pdf":
                    raw_text = PdfExtractor.extract_text_from_pdf(file_path)
                    processed_text = TextParser.process(raw_text)
                    full_text += f"\n\n--- Texto processado e extraído de {file_path.name} ---\n{processed_text}"
                    processed_files.append(file_path.name)
                case ".docx":
                    raw_text = DocxExtractor.extract_text_from_docx(file_path)
                    processed_text = TextParser.process(raw_text)
                    full_text += f"\n\n--- Texto extraído de {file_path.name} ---\n{processed_text}"
                    processed_files.append(file_path.name)
                case ".doc":
                    raw_text = DocExtractor.extract_text_from_doc(file_path)
                    processed_text = TextParser.process(raw_text)
                    full_text += f"\n\n--- Texto processado e extraído de {file_path.name} ---\n{processed_text}"
                    processed_files.append(file_path.name)
                case ".odt":
                    raw_text = OdtExtractor.extract_text_from_odt(file_path)
                    processed_text = TextParser.process(raw_text)
                    full_text += f"\n\n--- Texto processado e extraído de {file_path.name} ---\n{processed_text}"
                    processed_files.append(file_path.name)
                case ".xls" | ".xlsx" | ".ods":
                    raw_text = SpreadsheetExtractor.extract_text_from_spreadsheet(file_path, file_extension=file_ext)
                    processed_text = TextParser.process(raw_text)
                    full_text += f"\n\n--- Texto processado e extraído de {file_path.name} ---\n{processed_text}"
                    processed_files.append(file_path.name)
                case ".zip":
                    file_name = FileManager.get_file_name(file_path)
                    extract_folder = folder_path / file_name
                    ZipExtractor.extract_zip_file(file_path, extract_folder)
                    # Chamada recursiva para extrair o conteúdo do ZIP
                    full_text, processed_files = AttachmentReader.read_attachment(extract_folder, processed_files, full_text)
            

        if not processed_files:
            logger.warning(f"Nenhum arquivo de anexo processado na pasta: {folder_path}")

        return full_text, processed_files