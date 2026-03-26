import logging
import sys
from pathlib import Path

class ColoredFormatter(logging.Formatter):
    """Formatação de log colorida para melhorar a legibilidade no console."""
    COLOR_CODES = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[0m",   # Default
        logging.WARNING: "\033[33m",# Yellow
        logging.ERROR: "\033[31m",  # Red
    }
    RESET_CODE = "\033[0m"

    def format(self, record):
        color_code = self.COLOR_CODES.get(record.levelno, self.RESET_CODE)
        formatted_message = super().format(record)
        return f"{color_code}{formatted_message}{self.RESET_CODE}"

class LoggingService:
    @staticmethod
    def setup_logging(name: str = "licitacoes", log_file: str = "results/processing.log") -> logging.Logger:
        """
        Configura o logging centralizado para o projeto.
        Loga tanto no console (INFO) quanto em um arquivo (DEBUG).
        """
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if logger.handlers:
            return logger

        formatter = ColoredFormatter(
            "%(levelname)s | %(name)s | %(message)s"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Retorna um logger para o módulo específico."""
        return logging.getLogger(f"licitacoes.{name}")