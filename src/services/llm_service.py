import os
from openai import OpenAI
from typing import List

from src.utils.logging_utils import LoggingService
from src.models.schemas import Item

logger = LoggingService.get_logger("services.llm")

class LlmService:
    """Serviço responsável pela comunicação da LLM com os dados já processados."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", default="gpt-4o-mini")

    def extract_items(self, parsed_text: str) -> List[Item]:
        """Extrai itens de uma licitação a partir do texto processado usando a LLM."""
        pass