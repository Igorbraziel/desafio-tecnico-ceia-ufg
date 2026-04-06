import subprocess
from pathlib import Path
from src.utils.logging_utils import LoggingService

logger = LoggingService.get_logger("extractor.doc")

class DocExtractor:
    """Classe responsável por extrair texto de arquivos .doc legado usando antiword."""
    
    @staticmethod
    def extract_text_from_doc(file_path: Path) -> str:
        """Extrai texto rodando o utilitário antiword no SO."""
        if not file_path.exists() or not file_path.is_file():
            logger.warning(f"Arquivo DOC não encontrado: {file_path}")
            return ""

        logger.info(f"Começando extração de arquivo DOC: {file_path}")
        try:
            result = subprocess.run(
                ["antiword", "-m", "UTF-8", str(file_path)],
                capture_output=True,
                text=True,
                check=True
            )
            text = result.stdout.strip()
            
            if text:
                logger.info("Texto extraído com sucesso do arquivo DOC (utilizando antiword)")
                return text
            
            logger.warning(f"Nenhum texto extraído do arquivo DOC: {file_path.name}")
            return ""
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao extrair texto do DOC (antiword falhou) '{file_path.name}': {e.stderr}")
            return ""
        except FileNotFoundError:
            logger.warning("Utilitário 'antiword' não está instalado no sistema. Não é possível ler o DOC.")
            return ""
        except Exception as e:
            logger.error(f"Erro fatal ao processar o arquivo DOC '{file_path.name}': {e}")
            return ""
