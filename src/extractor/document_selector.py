from pathlib import Path
from typing import List, Tuple

from src.utils.logging_utils import LoggingService
from src.utils.file_utils import FileManager

logger = LoggingService.get_logger("extractor.document_selector")


class DocumentSelector:
    """Seleciona os documentos mais relevantes para extração de itens.
    
    Estratégia: Se documentos prioritários forem encontrados (edital, termo de referência,
    relação de itens), processa APENAS esses. Só recorre a outros documentos se nenhum
    prioritário estiver disponível.
    """
    
    PRIORITY_DOCUMENTS = [
        "termo_referencia",
        "termo_de_referencia",
        "termo_de_referncia",
        "termo",
        "edital",
        "edita",
        "relacaoitens",
    ]

    IGNORED_DOCUMENTS = [
        "contrato", "planilha_custos", "ata_registro", "imr",
        "atestado", "vistoria", "comprovante", "ata_de_sessao",
        "minuta_do_contrato", "minuta_de_contrato",
        "estudo_tcnico", "estudo_tecnico", "estudo_tcnico_preliminar",
        "modelo_de_proposta", "modelo_editavel",
        "declaracao", "concordancia",
        "planilha_de_co",
    ]

    @classmethod
    def _classify_file(cls, file_path: Path) -> Tuple[int, bool]:
        """Classifica um arquivo como prioritário ou não.

        Returns:
            Tupla (score, is_priority): score > 0 indica prioridade, is_priority indica se é um doc prioritário.
        """
        filename = file_path.name.lower()

        # Verifica se é um documento ignorado
        if any(ignored in filename for ignored in cls.IGNORED_DOCUMENTS):
            return -1, False

        # Verifica se é um documento prioritário
        for i, keyword in enumerate(cls.PRIORITY_DOCUMENTS):
            if keyword in filename:
                score = len(cls.PRIORITY_DOCUMENTS) - i
                return score, True

        # Documento não-prioritário, não-ignorado
        return 0, False

    @classmethod
    def select_best_documents(cls, folder_path: Path) -> List[Path]:
        """Retorna documentos para processar, priorizando docs de alta relevância.

        Estratégia:
        1. Se documentos prioritários forem encontrados → retorna apenas esses
        2. Se nenhum prioritário for encontrado → retorna todos os não-ignorados

        Args:
            folder_path: Pasta com os anexos de uma licitação

        Returns:
            Lista com os documentos selecionados, ordenados por prioridade
        """
        priority_docs: List[Tuple[int, Path]] = []
        fallback_docs: List[Path] = []

        for file_path in folder_path.iterdir():
            if not FileManager.verify_file_exists(file_path):
                continue

            score, is_priority = cls._classify_file(file_path)

            if score == -1:
                logger.debug(f"Documento ignorado (irrelevante): {file_path.name}")
                continue

            if is_priority:
                priority_docs.append((score, file_path))
            else:
                fallback_docs.append(file_path)

        # Decisão: usar prioritários ou fallback
        if priority_docs:
            priority_docs.sort(reverse=True)
            selected = [fp for _, fp in priority_docs]
            logger.info(
                f"✅ {len(selected)} documento(s) prioritário(s) encontrado(s). "
                f"Ignorando {len(fallback_docs)} documento(s) secundário(s)."
            )
            for _, fp in priority_docs:
                logger.debug(f"  ↳ Prioritário: {fp.name}")
            return selected
        else:
            logger.warning(
                f"⚠️ Nenhum documento prioritário encontrado. "
                f"Usando {len(fallback_docs)} documento(s) secundário(s) como fallback."
            )
            return fallback_docs