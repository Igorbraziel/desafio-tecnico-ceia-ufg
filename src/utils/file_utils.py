from pathlib import Path

class FileManager:
    @staticmethod
    def get_folder_path(json_path: Path) -> Path:
        return Path(json_path.stem)
        