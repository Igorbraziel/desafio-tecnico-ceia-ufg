import filetype
from pathlib import Path

class FileManager:
    @staticmethod
    def get_file_name(file_path: Path) -> str:
        return file_path.stem

    @staticmethod
    def guess_file_extension(file_path: Path) -> str:
        """Descobre a extensão real de um arquivo lendo seus bytes"""
        try:
            kind = filetype.guess(file_path)
            if kinf is not None:
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