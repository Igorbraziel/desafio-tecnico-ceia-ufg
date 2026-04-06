"""Parser para o campo 'itens' do JSON, extraindo dados estruturados de strings semi-formatadas."""
import re
from typing import List, Optional, Tuple
from src.utils.logging_utils import LoggingService

logger = LoggingService.get_logger("parser.item_parser")


class ItemParser:
    """Responsável por parsear o campo 'itens' semi-estruturado do JSON de entrada."""

    ITEM_PATTERN = re.compile(
        r'(\d+)\s*-\s*' # Número do item
        r'(.+?)' # Nome/título do item (até Tratamento ou Quantidade)
        r'(?:Tratamento\s+Diferenciado.*?)?'  # Skip tratamento
        r'(?:Aplicabilidade.*?)*?'     # Skip aplicabilidade
        r'Quantidade:\s*(\d+)'         # Quantidade
        r'.*?'                         # Skip qualquer coisa
        r'Unidade\s+de\s+fornecimento:\s*(.+?)' # Unidade
        r'\s*(?:\r?\n|----------|\Z)',  # Fim do item
        re.DOTALL | re.IGNORECASE
    )

    @classmethod
    def parse_itens_field(cls, itens_raw: List[str]) -> List[dict]:
        """Parseia a lista de strings brutas do campo 'itens' do JSON.

        Args:
            itens_raw: Lista de strings do campo data.itens do JSON

        Returns:
            Lista de dicionários com item, objeto, quantidade, unidade_fornecimento
        """
        if not itens_raw:
            return []

        full_text = "\n".join(itens_raw)
        full_text = full_text.replace("\r\n", "\n").replace("\r", "\n")
        
        items = []
        matches = cls.ITEM_PATTERN.findall(full_text)
        
        for match in matches:
            item_num, descricao, quantidade, unidade = match
            
            descricao = re.sub(r'\s+', ' ', descricao).strip()
            descricao = re.sub(r'\s*Tratamento\s+Diferenciado.*$', '', descricao, flags=re.IGNORECASE).strip()
            descricao = re.sub(r'\s*Aplicabilidade.*$', '', descricao, flags=re.IGNORECASE).strip()
            
            unidade = unidade.strip()
            
            items.append({
                "item": int(item_num),
                "objeto": descricao,
                "quantidade": int(quantidade),
                "unidade_fornecimento": unidade
            })

        logger.info(f"ItemParser: {len(items)} itens extraídos do campo JSON 'itens'.")
        return items

    @classmethod
    def format_scaffold_for_prompt(cls, parsed_items: List[dict]) -> str:
        """Formata os itens parseados como referência para o prompt da LLM.

        Args:
            parsed_items: Lista de itens parseados pelo parse_itens_field

        Returns:
            String formatada para inclusão no prompt da LLM
        """
        if not parsed_items:
            return ""

        lines = [f"Total de itens esperados: {len(parsed_items)}"]
        
        # Padrão para capturar nomes de itens repetidos no início
        name_pattern = re.compile(r"^(.+?)\s+\1\b", re.IGNORECASE)
        
        for item in parsed_items:
            # Extrai o nome limpo se ele for repetido no início do objeto
            objeto = item.get('objeto', '')
            match = name_pattern.search(objeto)
            
            if match:
                nome = match.group(1)
            else:
                nome = objeto
                if len(nome) > 80:
                    nome = nome[:77] + "..."
                    
            lines.append(
                f"Item {item['item']} | Nome: {nome} | Qtd: {item['quantidade']}"
            )

        return "\n".join(lines)

    @classmethod
    def parse_and_format(cls, itens_raw: List[str]) -> Tuple[List[dict], str]:
        """Método combinado: parseia e formata em um só passo.

        Returns:
            Tupla (itens_parseados, texto_formatado_para_prompt)
        """
        parsed = cls.parse_itens_field(itens_raw)
        formatted = cls.format_scaffold_for_prompt(parsed)
        return parsed, formatted
