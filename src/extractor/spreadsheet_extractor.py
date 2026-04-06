"""Extração de texto de planilhas (XLS, XLSX, ODS) utilizando pandas."""
import pandas as pd
from pathlib import Path
from typing import Literal, Any

from src.utils.logging_utils import LoggingService

logger = LoggingService.get_logger("extractor.spreadsheet")
    
class SpreadsheetExtractor:
    """Classe responsável por extrair texto de arquivos de planilha (XLS, XLSX, ODS) utilizando pandas."""

    SPREADSHEET_ENGINE_MAP = {
        ".xls":  "xlrd",
        ".xlsx": "openpyxl",
        ".ods":  "odf",
    }
    
    @staticmethod
    def extract_text_from_spreadsheet(file_path: Path, file_extension: Literal[".xls", ".xlsx", ".ods"]) -> str:
        """Extrai texto de um arquivo de planilha. Retorna o texto extraído ou uma string vazia em caso de falha."""
        engine = SpreadsheetExtractor.SPREADSHEET_ENGINE_MAP.get(file_extension)

        try:
            sheets = pd.read_excel(file_path, sheet_name=None, header=None, engine=engine)  # type: ignore
            logger.debug(f"Planilha lida com sucesso: {file_path} | ext: {file_extension}")
        except Exception as e:
            logger.error(f"Pandas falhou na leitura da planilha: {file_path}\n Erro: {e}")
            raise RuntimeError("Pandas falhou:", e)

        lines = []
        for sheet_name, dataframe in sheets.items():
            dataframe = dataframe.fillna("").astype(str)

            for _, row in dataframe.iterrows():
                columns = [col.strip() for col in row if col.strip()]
                if columns:
                    lines.append(" | ".join(columns))

        if not lines:
            logger.warning(f"Nenhum texto extraído da planilha: {file_path}")
            return ""

        return "\n".join(lines)
        
