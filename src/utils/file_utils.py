from pathlib import Path

class FileManager:
    @staticmethod
    def get_file_name(file_path: Path) -> str:
        return file_path.stem
        
    @staticmethod 
    def get_file_extension(file_path: Path) -> str:
        return file_path.suffix.lower()