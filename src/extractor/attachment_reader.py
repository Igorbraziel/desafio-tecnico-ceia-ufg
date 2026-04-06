from pathlib import Path
from typing import Tuple, List, Optional

from src.utils.logging_utils import LoggingService
from src.utils.file_utils import FileManager

from src.extractor.pdf_extractor import PdfExtractor
from src.extractor.docx_extractor import DocxExtractor
from src.extractor.spreadsheet_extractor import SpreadsheetExtractor
from src.extractor.zip_extractor import ZipExtractor
from src.extractor.doc_extractor import DocExtractor
from src.extractor.odt_extractor import OdtExtractor
from src.extractor.document_selector import DocumentSelector
from src.parser.text_parser import TextParser

logger = LoggingService.get_logger("extractor.attachment")

class AttachmentReader:
    """Classe responsável por ler e extrair texto dos anexos de uma licitação.
    
    Aplica isolamento de seção por documento para remover texto jurídico
    antes de concatenar os textos.
    """
    SUPPORTED_FILE_TYPES = [
        ".pdf",
        ".docx",
        ".xls",
        ".xlsx",
        ".ods",
        ".zip",
        ".doc",
        ".odt",
    ]

    @staticmethod
    def _extract_text_from_file(file_path: Path, file_ext: str) -> str:
        """Extrai texto bruto de um arquivo baseado na sua extensão."""
        match file_ext:
            case ".pdf":
                return PdfExtractor.extract_text_from_pdf(file_path)
            case ".docx":
                return DocxExtractor.extract_text_from_docx(file_path)
            case ".doc":
                return DocExtractor.extract_text_from_doc(file_path)
            case ".odt":
                return OdtExtractor.extract_text_from_odt(file_path)
            case ".xls" | ".xlsx" | ".ods":
                return SpreadsheetExtractor.extract_text_from_spreadsheet(file_path, file_extension=file_ext)
            case _:
                logger.warning(f"Extensão de arquivo não permitida: {file_ext}")
                return ""

    @classmethod
    def read_attachment(cls, folder_path: Path, processed_files: Optional[List[str] | None] = None, full_text: str = "") -> Tuple[str, List[str]]:
        """
        Extrai e concatena texto de todos os anexos relevantes de uma licitação.
        
        Aplica isolamento de seção em cada documento individualmente para remover
        boilerplate e preservar apenas o conteúdo relevante para extração de itens.
        
        Retorna (texto_completo, lista_de_arquivos_processados).
        """
        if not folder_path.exists() or not folder_path.is_dir():
            logger.info(f"Pasta de anexos não encontrada: {folder_path}")
            return "", []

        if not processed_files:
            processed_files = []

        if not full_text:
            full_text = ""
            
        relevant_file_paths = DocumentSelector.select_best_documents(folder_path)

        for file_path in relevant_file_paths:
            if file_path.is_dir():
                continue
                
            if not FileManager.verify_file_exists(file_path):
                logger.warning(f"Arquivo de anexo não encontrado: {file_path.name}")
                continue

            file_ext = FileManager.get_file_extension(file_path)

            if not file_ext or file_ext not in cls.SUPPORTED_FILE_TYPES:
                guess_extension = FileManager.guess_file_extension(file_path)

                if guess_extension in cls.SUPPORTED_FILE_TYPES:
                    logger.info(f"Extensão do arquivo '{file_path.name}' corrigida para '{guess_extension}' com base na análise de conteúdo.")

                    file_ext = guess_extension
                    new_file_path = file_path.with_name(f"{file_path.name}{file_ext}")
                    file_path.rename(new_file_path)
                    file_path = new_file_path
                else:
                    logger.warning(f"Extensão do arquivo ({file_ext if file_ext else guess_extension}) '{file_path.name}' não encontrada ou arquivo não suportado!")
                    continue

            # Tratamento especial para ZIP: extrai e processa recursivamente
            if file_ext == ".zip":
                file_name = FileManager.get_file_name(file_path)
                extract_folder = folder_path / file_name
                ZipExtractor.extract_zip_file(file_path, extract_folder)
                full_text, processed_files = cls.read_attachment(extract_folder, processed_files, full_text)
                continue

            raw_text = cls._extract_text_from_file(file_path, file_ext)
            
            if not raw_text or not raw_text.strip():
                logger.warning(f"Nenhum texto extraído de: {file_path.name}")
                continue

            processed_text = TextParser.clean_raw_text(raw_text)
            
            if len(processed_text) > 2000:
                isolated_text = TextParser.isolate_items_section(processed_text)
                if len(isolated_text) < len(processed_text):
                    logger.info(f"Seção isolada em {file_path.name}: {len(processed_text)} → {len(isolated_text)} chars")
                    processed_text = isolated_text

            full_text += f"\n\n--- Texto extraído de {file_path.name} ---\n{processed_text}"
            processed_files.append(FileManager.clean_filename(filename=file_path.name))
        
        if not processed_files:
            logger.warning(f"Nenhum arquivo de anexo processado na pasta: {folder_path}")

        return full_text, processed_files