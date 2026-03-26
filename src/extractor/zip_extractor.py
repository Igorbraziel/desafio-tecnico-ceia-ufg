import zipfile

from pathlib import Path
from src.utils.logging_utils import LoggingService

logger = LoggingService.get_logger("extractor.zip")

class ZipExtractor:
    """Classe responsável por extrair arquivos ZIP."""
    @staticmethod
    def extract_zip_file(zip_path: Path, extract_to: Path):
        """Extrai um arquivo ZIP para um diretório especificado."""
        if not zip_path.exists() or not zip_path.is_file():
            logger.warning(f"Arquivo ZIP não encontrado: {zip_path}")
            return

        extract_to.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                try:
                    zip_ref.extract(file_info, extract_to)
                    logger.info(f"Arquivo extraído '{file_info.filename}' para '{extract_to}'")
                except zipfile.BadZipFile as e:
                    logger.error(f"Erro de integridade (CRC/Corrompido) no arquivo '{file_info.filename}': {e}")
                except Exception as e:
                    logger.error(f"Erro inesperado ao extrair '{file_info.filename}': {e}")