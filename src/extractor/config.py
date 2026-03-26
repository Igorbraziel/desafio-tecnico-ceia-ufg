class Config:
    """Classe de configuração para o processo de extração de dados de licitações."""
    SUPPORTED_FILE_TYPES = [
        ".pdf",
        ".docx",
        ".xls",
        ".xlsx",
        ".ods",
        ".zip",
        ".doc",
        ".odt",
    ]

    SPREADSHEET_ENGINE_MAP = {
        ".xls":  "xlrd",
        ".xlsx": "openpyxl",
        ".ods":  "odf",
    }