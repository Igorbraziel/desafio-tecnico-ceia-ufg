import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from src.utils.file_utils import FileManager

logger = logging.getLogger(__name__)

class JsonReader:
    @staticmethod
    def extract_folder_info(downloads_dir: Path) -> List[Dict[str, Any]]:
        info_list = []
        for file_path in downloads_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        dir_path = FileManager.get_folder_path(file_path)
                        info_list.append({
                            "dir_path": dir_path,
                            "json_data": data
                        })
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Erro ao processar o arquivo JSON '{file_path}': {e}")
            
        return info_list