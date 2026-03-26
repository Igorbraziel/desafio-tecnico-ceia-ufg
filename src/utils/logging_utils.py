import logging
import sys
from pathlib import Path

class LogService:
    """Serviço de logging para o projeto"""
    def __init__(self, name: str, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

    def info(self, message: str):
        """Utilizado para monstrar informações gerais sobre o andamento do processo."""
        self.logger.info(message)

    def warning(self, message: str):
        """Utilizado para mostrar avisos sobre situações não padrão."""
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False):
        """Utilizado para mostrar erros graves que impedem o sistema de funcionar corretamente."""
        self.logger.error(message, exc_info=exc_info)

logging_service = LogService(name="Logger", level=logging.INFO)