import re
from typing import List
from src.utils.logging_utils import LoggingService
import unicodedata


logger = LoggingService.get_logger("parser.text_parser")


class TextParser:
    """Classe responsável por limpar e fatiar textos brutos extraídos de arquivos."""

    @staticmethod
    def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
        """Divide texto em chunks com overlap, quebrando em limites de parágrafo quando possível.

        Args:
            text: texto a ser dividido
            chunk_size: tamanho máximo de cada chunk
            overlap: sobreposição entre chunks

        Returns:
            Lista dos chunks extraídos
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)

            if end < text_length:
                paragraph_break = text.rfind("\n\n", start + chunk_size // 2, end)
                if paragraph_break > start:
                    end = paragraph_break
                else:
                    line_break = text.rfind("\n", start + chunk_size // 2, end)
                    if line_break > start:
                        end = line_break
                    else:
                        space_break = text.rfind(" ", start + chunk_size // 2, end)
                        if space_break > start:
                            end = space_break

            chunks.append(text[start:end])

            start = max(start + 1, end - overlap) if end < text_length else text_length

        return chunks

    @staticmethod
    def clean_raw_text(text: str) -> str:
        """Aplica regras de Regex para limpar texto extraído de arquivos."""
        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text)

        # 1. Remove caracteres de controle ASCII
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # 2. Remove repetições de pontos
        text = re.sub(r'\.{4,}', '...', text)

        # 3. Remove espaços em branco horizontais desnecessários
        text = re.sub(r'[ \t]+', ' ', text)

        # 4. Normaliza quebras de linha
        text = re.sub(r'\r\n?', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 5. Conserta palavras quebradas em linhas (hifenização de PDF)
        text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

        # 6. Remove espaços entre pontuações
        text = re.sub(r'\s+([,.;:])', r'\1', text)
        text = re.sub(r'([,;:])([^\s\d,;:])', r'\1 \2', text)

        # 7. Remove espaços vazios no início e fim de cada linha
        text = re.sub(r'(?m)^[ \t]+|[ \t]+$', '', text)

        return text.strip()

    @staticmethod
    def isolate_items_section(text: str) -> str:
        """Tenta isolar a seção de itens, cortando lixo do início."""
        
        original_len = len(text)
        if original_len < 2000:
            return text


        # Âncoras de início da seção de itens (ordenadas por especificidade)
        start_anchors = [
            # O clássico do Compras.gov.br
            r"1\s*-\s*Itens\s+da\s+Licitação",
            r"relação\s+de\s+itens",

            # Tabela de itens com cabeçalho
            r"(?:lote|grupo|item)[\s\S]{0,30}(?:descrição|especificação|objeto)[\s\S]{0,30}(?:quant|qtd|unid)",

            # Cabeçalho tabulado de itens (formato planilha)
            r"ITEM\s*\|\s*ESPECIFICAÇÃO",
            r"código[\s\S]{0,20}descrição[\s\S]{0,20}unidade",

            # Anexos com Termo de Referência
            r"anexo\s+[IVX\d]+\s*[-–]?\s*(?:termo\s+de\s+referência|modelo\s+de\s+proposta|especificações)",

            # Seções do Termo de Referência
            r"descrição\s+(?:detalhada\s+)?do\s+objeto",
            r"mapa\s+de\s+preços?",
        ]

        start_pattern = re.compile("|".join(start_anchors), re.IGNORECASE)
        start_match = start_pattern.search(text)

        sliced_text = text

        if start_match:
            start_idx = max(0, start_match.start() - 200)
            sliced_text = text[start_idx:]
            logger.info(f"Corte inicial aplicado. Âncora: '{start_match.group()[:50]}'")
        else:
            logger.warning("Nenhuma âncora de início encontrada. Usando texto completo.")

        return sliced_text[:300000]