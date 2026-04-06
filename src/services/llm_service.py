import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from typing import List

from src.utils.logging_utils import LoggingService
from src.parser.text_parser import TextParser
from src.models.schemas import ItemList, Item

load_dotenv()

logger = LoggingService.get_logger("services.llm")

class LlmService:
    """Serviço responsável pela comunicação da LLM com os dados já processados."""
    
    MAX_SINGLE_CALL_CHARS = 200_000
    CHUNK_SIZE = 180_000
    CHUNK_OVERLAP = 10_000

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", default="gpt-5-mini")

    def _build_system_prompt(self, has_scaffold: bool) -> str:
        """Constrói o prompt de sistema em português."""

        prompt = """Você é um assistente especializado em licitações públicas brasileiras.
        Sua missão é extrair a relação COMPLETA de itens licitados a partir do texto dos DOCUMENTOS fornecidos (edital, termo de referência, relação de itens, etc.).
        
        ATENÇÃO/CRÍTICO: Você está ESTRITAMENTE PROIBIDO de alucinar, adivinhar ou inventar qualquer informação. Utilize EXCLUSIVAMENTE o conteúdo extraído e fornecido no texto do documento. Nunca adicione informações baseadas em seu conhecimento prévio.

        REGRAS DE EXTRAÇÃO:
        1. 'lote': Grupo ou lote ao qual o item pertence. Deve aparecer explicitamente como "Grupo 1", "G1", "GRUPO I", "Lote 1", etc.
           - A seção de "Grupos" (quando presente) geralmente aparece ao FINAL da relação de itens e mapeia quais itens pertencem a qual grupo.
           - NUNCA utilize o número do item como lote. Se o texto não indicar claramente um agrupamento em lotes ou grupos para o item, retorne null.
        2. 'item': O número EXATO do item conforme impresso no texto. não invente sequências.
        3. 'objeto': A descrição COMPLETA e DETALHADA do item conforme aparece no edital, termo de referência ou relação de itens.
           - COPIE a descrição EXATAMENTE como ela aparece no documento, incluindo TODAS as especificações técnicas.
        4. 'quantidade': Quantidade solicitada do item (inteiro).
        5. 'unidade_fornecimento': A unidade conforme aparece no documento (ex: "Unidade", "Serviço", "Caixa 50,00 UN", "Pacote 500,00 FL").

        INSTRUÇÕES IMPORTANTES:
        - Se o texto começar no meio de uma descrição de item, ignore o fragmento inicial e comece do primeiro item completo.
        - Extraia TODOS os itens encontrados no texto. Não omita nenhum item.
        - Mantenha a numeração EXATA dos itens como aparece no documento.
        - Para a descrição (objeto), copie o texto do documento da forma mais fiel e completa possível.
        - CRÍTICO: Os documentos com a descrição mais detalhada e correta aparecem no inícío do texto. Se o mesmo número de item aparecer várias vezes ao longo do texto fornecido, EXTRAIA E UTILIZE SEMPRE A PRIMEIRA OCORRÊNCIA que encontrar.
        - Ignore textos jurídicos, cláusulas contratuais ou regras do edital que estejam misturados.
        - Retorne os dados estritamente no formato JSON solicitado."""

        if has_scaffold:
            prompt += """

                REFERÊNCIA DE CONTAGEM (EXTRAÍDA DO SISTEMA DE COMPRAS):
                Abaixo está uma lista com os NÚMEROS dos itens, seus NOMES resumidos e QUANTIDADES esperadas nesta licitação.
                
                EXTREMO CUIDADO E ATENÇÃO: Esta referência NÃO É A FONTE VERDADEIRA DOS DADOS e DEVE SER USADA APENAS COMO UM GUIA DE CONFERÊNCIA.
                - É EXPRESSAMENTE PROIBIDO COPIAR o nome resumido desta referência para o seu campo 'objeto'.
                - Você DEVE buscar e copiar a descrição COMPLETA ('objeto'), a 'unidade_fornecimento' e o 'lote' DIRETAMENTE do texto principal dos documentos da licitação.
                - A referência serve APENAS para te ajudar a saber quantos itens existem e localizar os itens nos documentos. A descrição real e detalhada de cada item está no texto dos documentos, e é de lá que você deve extrair o 'objeto'.
            """

        return prompt

    def _build_user_prompt(self, document_text: str, scaffold: str = "",
                           chunk_index: int = 0, total_chunks: int = 1) -> str:
        """Constrói o prompt do usuário com o texto do documento e scaffold de referência."""
        parts = []

        if scaffold:
            parts.append(
                "=== REFERÊNCIA DE CONTAGEM (NÚMEROS, NOMES E QUANTIDADES) ===\n"
                f"{scaffold}\n"
                "=== FIM DA REFERÊNCIA ===\n"
            )

        # Adiciona contexto de chunk quando há múltiplos chunks
        if total_chunks > 1:
            parts.append(
                f"⚠️ ATENÇÃO: Este é o trecho {chunk_index}/{total_chunks} do documento.\n"
                "Extraia SOMENTE os itens cujas descrições aparecem NESTE trecho de texto.\n"
                "NÃO repita itens que não estejam presentes neste trecho.\n"
                "IMPORTANTE: Você pode estar recebendo apenas uma parte do documento completo.\n"
            )
        else:
            parts.append(
                "⚠️ ATENÇÃO: Você pode estar recebendo apenas uma parte do documento completo.\n"
                "Se este texto parecer incompleto ou cortado, extraia apenas os itens que estão claramente presentes.\n"
            )

        parts.append(
            "=== TEXTO DOS DOCUMENTOS DA LICITAÇÃO (EXTRAIA AS DESCRIÇÕES DAQUI) ===\n"
            f"{document_text}\n"
            "=== FIM DO TEXTO ==="
        )

        return "\n\n".join(parts)

    def _call_llm(self, user_prompt: str, has_scaffold: bool, context_instruction: str = "") -> ItemList | None:
        """Realiza a chamada da LLM."""
        system_prompt = self._build_system_prompt(has_scaffold)

        if context_instruction:
            system_prompt = f"{system_prompt}\n\n{context_instruction}"

        try:
            logger.info(f"Enviando texto para LLM ({len(user_prompt)} caracteres)")

            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=ItemList,
            )

            result = response.choices[0].message.parsed
            if result:
                logger.info(f"LLM retornou {len(result.itens_extraidos)} itens")
            return result

        except Exception as e:
            logger.error(f"Erro ao extrair itens utilizando a LLM: {e}")
            return None

    def _deduplicate_items(self, items: List[Item]) -> List:
        """Remove itens duplicados usando uma chave única composta por ('item' e 'lote').
        
        Quando duplicatas são encontradas (mesmo 'item' e 'lote'), mantém a versão 
        encontrada primeiro.
        """
        if not items:
            return []

        # Dicionário onde a chave é uma tupla (item, lote)
        unique_items_dict = {}
        
        for item in items:
            key = (item.item, item.lote)
            if key not in unique_items_dict:
                # Primeira ocorrência do item
                unique_items_dict[key] = item
            else:
                # Duplicata encontrada: mantém a versão que apareceu primeiro
                existing = unique_items_dict[key]
                logger.debug(
                    f"Dedup: item {item.item}, lote {item.lote} duplicado detectado; mantendo a primeira ocorrência "
                    f"(não substituindo por item do chunk seguinte)."
                )
        
        # Reconstrói a lista: itens com chave (ordenados por item, depois lote), seguidos pelos itens sem chave
        result = sorted(unique_items_dict.values(), key=lambda x: (x.item, x.lote or ""))
        
        if len(result) < len(items):
            logger.info(f"Deduplicação por número de item: {len(items)} → {len(result)} itens")
        
        return result

    @staticmethod
    def _get_expected_count(scaffold: str) -> int | None:
        """Extrai o número esperado de itens a partir do scaffold.
        
        Procura pelo padrão 'Total de itens esperados: N' no scaffold.
        """
        if not scaffold:
            return None
        match = re.search(r'Total de itens esperados:\s*(\d+)', scaffold)
        return int(match.group(1)) if match else None

    def extract_items(self, parsed_text: str, scaffold: str = "") -> ItemList | None:
        """Extrai itens de uma licitação a partir do texto processado usando a LLM.
        
        Args:
            parsed_text: Texto combinado e processado dos documentos da licitação
            scaffold: Referência mínima dos itens do JSON (números, nomes e quantidades)
        
        Returns:
            ItemList com os itens extraídos ou None
        """
        if not parsed_text:
            logger.warning("Texto processado vazio. Nenhum item para extrair.")
            return None

        has_scaffold = bool(scaffold)
        text_length = len(parsed_text) + len(scaffold)

        if text_length <= self.MAX_SINGLE_CALL_CHARS:
            logger.info("Texto cabe em chamada única. Enviando tudo de uma vez.")
            user_prompt = self._build_user_prompt(parsed_text, scaffold)
            return self._call_llm(user_prompt, has_scaffold)

        # Chunking como fallback para documentos gigantes
        logger.warning(f"Documento grande ({text_length} chars). Dividindo em chunks.")
        
        chunks = TextParser.chunk_text(
            text=parsed_text,
            chunk_size=self.CHUNK_SIZE,
            overlap=self.CHUNK_OVERLAP
        )

        expected_count = self._get_expected_count(scaffold)
        master_item_list = ItemList(itens_extraidos=[])
        total_chunks = len(chunks)
        chunks_processed = 0
        last_known_item_num = None
        last_known_lote = None
        logger.info(f"Dividido em {total_chunks} chunks para extração.")

        if expected_count:
            logger.info(f"Total esperado de itens (do scaffold): {expected_count}")

        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processando chunk {i}/{total_chunks}...")

            context_instruction = ""
            if i > 1 and last_known_item_num is not None:
                context_instruction = (
                    "⚠️ CONTEXTO DE CONTINUAÇÃO: Este trecho é continuação do documento anterior. "
                    f"O último lote conhecido foi '{last_known_lote}', e o último item conhecido foi '{last_known_item_num}'. "
                    "VOCÊ NÃO DEVE RESETAR a contagem para 1, a menos que haja indicação clara de novo lote/tabela. "
                    "Mantenha a sequência real do documento."
                )

            user_prompt = self._build_user_prompt(
                chunk, scaffold,
                chunk_index=i, total_chunks=total_chunks
            )
            chunk_result = self._call_llm(user_prompt, has_scaffold, context_instruction=context_instruction)

            if chunk_result and chunk_result.itens_extraidos:
                master_item_list.itens_extraidos.extend(chunk_result.itens_extraidos)
                chunks_processed += 1

                # Atualiza o estado com o último item válido do chunk
                for item in reversed(chunk_result.itens_extraidos):
                    if item is not None and getattr(item, 'item', None) is not None:
                        last_known_item_num = item.item
                        last_known_lote = item.lote
                        break

            # Early stop: se já temos todos os itens esperados, não precisa continuar
            current_count = len(master_item_list.itens_extraidos)
            if expected_count and current_count >= expected_count:
                if i < total_chunks:
                    logger.info(
                        f"Early stop: {current_count} itens coletados "
                        f"(esperado: {expected_count}). Pulando {total_chunks - i} chunk(s) restante(s)."
                    )
                break

        # Deduplicação
        if chunks_processed > 1 and master_item_list.itens_extraidos:
            master_item_list.itens_extraidos = self._deduplicate_items(
                master_item_list.itens_extraidos
            )

        logger.info(f"Extração total concluída: {len(master_item_list.itens_extraidos)} itens consolidados.")
        return master_item_list