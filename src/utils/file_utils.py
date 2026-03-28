import filetype
import json
from pathlib import Path
from typing import List, Dict, Any

from src.utils.logging_utils import LoggingService

logger = LoggingService.get_logger("utils.file_utils")

class FileManager:
    @staticmethod
    def get_file_name(file_path: Path) -> str:
        return file_path.stem

    @staticmethod
    def guess_file_extension(file_path: Path) -> str:
        """Descobre a extensão real de um arquivo lendo seus bytes"""
        try:
            kind = filetype.guess(file_path)
            if kind is not None:
                return f".{kind.extension}"
        except Exception as e:
            logger.warning(f"Erro ao tentar adivinhar extensão do arquivo {file_path.name}: {e}")
        return ""
        
    @staticmethod 
    def get_file_extension(file_path: Path) -> str:
        return file_path.suffix.lower()

    @staticmethod
    def verify_file_has_content(file_path: Path) -> bool:
        return file_path.stat().st_size > 0

    @staticmethod
    def verify_file_exists(file_path: Path) -> bool:
        return file_path.exists() and file_path.is_file()
    
    @staticmethod
    def write_final_result(final_result: List[Dict[str, Any]], result_path: Path = Path("results/resultado.json")):
        result_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(final_result, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ {len(final_result)} registros salvos em '{result_path}'")
        except Exception as e:
            logger.error(f"Erro fatal ao escrever o resultado final no arquivo: {result_path}. Detalhes: {e}")