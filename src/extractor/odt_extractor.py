"""Extração de texto de arquivos OpenDocument Text (.odt)."""
from pathlib import Path
from odf.opendocument import load  # type: ignore
from odf.teletype import extractText  # type: ignore
from odf import text as odf_text  # type: ignore
import zipfile

from src.utils.logging_utils import LoggingService
from src.utils.file_utils import FileManager

logger = LoggingService.get_logger("extractor.odt")

class OdtExtractor:
    """Classe responsável por extrair texto de arquivos OpenDocument Text (.odt)."""
    
    @staticmethod
    def extract_text_from_odt(file_path: Path) -> str:
        """Extrai texto de um arquivo ODT mantendo a ordem dos parágrafos e cabeçalhos."""
        if not FileManager.verify_file_exists(file_path):
            logger.warning(f"Arquivo ODT não encontrado: {file_path.name}")
            return ""

        if not FileManager.verify_file_has_content(file_path):
            logger.warning(f"Arquivo ODT está vazio (0 Bytes): {file_path.name}")
            return ""

        if not zipfile.is_zipfile(file_path):
            logger.error(f"Arquivo ODT inválido (formato real não é um ODT válido): {file_path.name}")
            return ""

        logger.debug(f"Começando extração de arquivo ODT: {file_path.name}")

        try:
            document = load(str(file_path))

            # Busca todos os elementos de Parágrafo (P) e Cabeçalho (H)
            text_elements = document.getElementsByType(odf_text.P) + document.getElementsByType(odf_text.H)

            extracted_texts = [extractText(element) for element in text_elements]

            text = "\n".join(extracted_texts).strip()
            
            if text:
                logger.debug("Texto extraído com sucesso do arquivo ODT")
                return text
            else:
                logger.warning(f"Nenhum texto extraído do arquivo ODT: {file_path.name}")
                return ""
                
        except Exception as e:
            logger.error(f"Erro ao extrair texto do ODT '{file_path.name}': {e}")
            return ""
