import os
from dotenv import load_dotenv
from openai import OpenAI

from src.utils.logging_utils import LoggingService
from src.models.schemas import ItemList

logger = LoggingService.get_logger("services.llm")
load_dotenv()

class LlmService:
    """Serviço responsável pela comunicação da LLM com os dados já processados."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", default="gpt-4o-mini")

    def extract_items(self, parsed_text: str) -> ItemList | None:
        """Extrai itens de uma licitação a partir do texto processado usando a LLM."""
        if not parsed_text:
            logger.warning("Texto processado vazio. Nenhum item para extrair.")
            return []
        
        system_prompt = """
        Você é um assistente especializado em licitações públicas brasileiras.
        Sua missão é extrair a relação de itens licitados do texto fornecido.
        
        REGRAS DE NEGÓCIO CRÍTICAS:
        1. 'lote': Lote ou Grupo a qual o item pertence(ex: "G1", "G2", "1", "2"). Se não houver agrupamento, retorne null.
        2. 'item': O número sequencial do item (inteiro, começando em 1).
        3. 'objeto': A descrição completa do item (incluindo categoria e especificações técnicas). Ignore textos jurídicos ou regras do edital que estejam misturados.
        4. 'quantidade': Quantidade solicitada do item.
        5. 'unidade_fornecimento': A sigla ou nome da unidade de fornecimento (ex: "Unidade" , "Caixa 50,00 UN" , "Pacote 500,00 FL" ).
        
        Você deve retornar os dados estritamente no formato JSON solicitado.
        """
        
        try:
            logger.info("Enviando texto processado para a LLM")
            
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": parsed_text}
                ],
                response_format=ItemList,
                temperature=0.1
            )
            
            logger.info("Extração realizada com sucesso")
            
            return response.choices[0].message.parsed
        except Exception as e:
            logger.error(f"Erro ao extrair itens de licitações utilizando a LLM: {e}")
            return None