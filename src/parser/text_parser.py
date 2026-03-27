import re
from src.utils.logging_utils import LoggingService

logger = LoggingService.get_logger("parser.text_parser")

class TextParser:
    """Classe responsável por limpar e fatiar textos brutos extraídos de arquivos."""

    @staticmethod
    def clean_raw_text(text: str) -> str:
        """
        Aplica regras de Regex para limpar texto extraído de arquivos.
        """
        if not text:
            return ""

        # 1. Remove caracteres de controle ASCII
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # 2. Remove repetições de pontos
        text = re.sub(r'\.{4,}', '...', text)

        # 3. Remove espaços em branco horizontais desnecessários
        text = re.sub(r'[ \t]+', ' ', text)

        # 4. Normaliza quebras de linha
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 5. Remove espaços vazios no início e fim de cada linha
        text = re.sub(r'(?m)^\s+|\s+$', '', text)

        return text.strip()

    @staticmethod
    def isolate_items_section(text: str) -> str:
        """
        Tenta isolar a seção de itens presente nos arquivos, cortando lixo do início e fime.
        """
        if len(text) < 2000:
            return text

        # Lista de âncoras comuns onde a relação de itens costuma começar
        start_anchors = [
            # O clássico do Compras.gov.br
            r"1\s*-\s*Itens\s+da\s+Licitação",
            r"relação\s+de\s+itens",

            # Anexos (Cobre "ANEXO I", "ANEXO 01", "ANEXO A")
            r"anexo\s+[IVX\d]+\s*[-–]?\s*(termo\s+de\s+referência|modelo\s+de\s+proposta|especificações)",

            # Seções do Termo de Referência
            r"especificaç[õo]es\s+técnicas",
            r"descrição\s+(detalhada\s+)?do\s+objeto",
            r"quadro\s+demonstrativo",
            r"planilha\s+orçamentária",
            r"mapa\s+de\s+preços?"
            # Procura a combinação de "Item", "Descrição" e "Quantidade" na mesma proximidade
            r"(lote|item)[\s\S]{0,30}(descrição|especificação|objeto)[\s\S]{0,30}(quant|qtd|unid)",

            # Padrão muito comum em planilhas exportadas para PDF
            r"código[\s\S]{0,20}descrição[\s\S]{0,20}unidade"
        ]

        # Lista de âncoras que indicam o fim da seção de itens
        stop_anchors = [
            r"das\s+obrigaç[õo]es\s+da\s+contratada",
            r"do\s+pagamento",
            r"da\s+entrega\s+e\s+recebimento",
            r"das\s+sanç[õo]es",
            r"da\s+dotação\s+orçamentária",
            r"local\s+de\s+entrega"
        ]

        start_pattern = re.compile("|".join(start_anchors), re.IGNORECASE)
        start_match = start_pattern.search(text)

        sliced_text = ""

        if start_match:
            # Deixa 50 caracteres antes da âncora (overlap chunking)
            start_idx = max(0, start_match.start() - 50)
            sliced_text = text[start_idx:]
            logger.info(f"Corte inicial aplicado. Início da seção de itens encontrada: '{start_match.group()}'")
        else:
            logger.warning("Nenhuma âncora de início de seção de itens encontrada. Analisando texto a partir do início.")

        stop_pattern = re.compile("|".join(stop_anchors), re.IGNORECASE)
        stop_match = stop_pattern.search(sliced_text)

        if stop_match:
            end_idx = start_match.start()
            final_text = sliced_text[:end_idx + 50]
            logger.info(f"Corte final aplicado. Fim da seção de itens encontrada: '{stop_match.group()}'")
        else:
            final_text = sliced_text
            logger.info("Nenhuma âncora encontrada no final da seção de itens.")
        
        return final_text[:40000]

    @classmethod
    def process(cls, raw_text: str) -> str:
        """Método principal que orquestra a limpeza e o fatiamento."""
        cleaned_text = cls.clean_raw_text(raw_text)
        final_text = cls.isolate_items_section(cleaned_text)
        return final_text