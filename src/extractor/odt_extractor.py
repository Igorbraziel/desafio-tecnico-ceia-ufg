from pathlib import Path
from odf.opendocument import load
from odf.teletype import extractText
from src.utils.logging_utils import LoggingService

logger = LoggingService.get_logger("extractor.odt")

class OdtExtractor:
    """Classe responsável por extrair texto de arquivos OpenDocument Text (.odt)."""
    
    @staticmethod
    def extract_text_from_odt(file_path: Path) -> str:
        if not file_path.exists() or not file_path.is_file():
            logger.warning(f"Arquivo ODT não encontrado: {file_path}")
            return ""

        logger.info(f"Começando extração de arquivo ODT: {file_path}")
        try:
            document = load(str(file_path))
            text = extractText(document).strip()
            
            if text:
                logger.info("Texto extraído com sucesso do arquivo ODT")
                return text
            else:
                logger.warning(f"Nenhum texto extraído do arquivo ODT: {file_path.name}")
                return ""
                
        except Exception as e:
            logger.error(f"Erro ao extrair texto do ODT '{file_path.name}': {e}")
            return ""
