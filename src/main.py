"""Módulo principal para execução do pipeline de extração de itens de licitação."""
import argparse
import sys
import time
from pathlib import Path
from typing import Any, Literal  # type: ignore

from src.utils.logging_utils import LoggingService
from src.utils.file_utils import FileManager
from src.extractor.json_extractor import JsonReader
from src.extractor.attachment_reader import AttachmentReader
from src.models.schemas import LicitacaoOutput, Item
from src.services.llm_service import LlmService
import pandas as pd  # type: ignore

def main() -> None:
    """Função principal que coordena a leitura de licitações, extração de anexos e chamada da LLM."""
    # Inicializa a configuração de Logging
    logger = LoggingService.setup_logging()
    final_result = []
    llm_service = LlmService()
    
    parser = argparse.ArgumentParser(description="Extração Estruturada de Itens de Licitações")
    parser.add_argument("--data-path", type=str, default="downloads/", help="Caminho para a pasta downloads/")
    
    args = parser.parse_args()
    
    data_path = Path(args.data_path)
    if not FileManager.verify_folder_exists(data_path):
        logger.error(f"Pasta '{data_path}' não encontrada.")
        sys.exit(1)
        
    logger.info(f"Iniciando processamento em: {data_path}")

    try:
        licitacao_list = JsonReader.extract_downloads_info(data_path)
        logger.info(f"Encontrados {len(licitacao_list)} processos para processar.")
    except Exception as e:
        logger.exception("Erro ao extrair informações do diretório de downloads.")
        sys.exit(1)

    start_time = time.time()
    total = len(licitacao_list)

    for i, licitacao in enumerate(licitacao_list, 1):
        logger.info(f"[{i}/{total}] Processando licitação: {licitacao.numero_pregao}")

        full_processed_text, processed_files = AttachmentReader.read_attachment(licitacao.pasta_anexos)

        logger.debug(f"Texto extraído (total de {len(full_processed_text)} caracteres)")
        logger.debug(f"Arquivos processados: {len(processed_files)}")
        
        extracted_items = []
        
        if full_processed_text:
            response = llm_service.extract_items(
                parsed_text=full_processed_text,
                scaffold=licitacao.itens_scaffold
            )
            
            if response:
                logger.info(f"Itens extraídos com sucesso: {len(response.itens_extraidos)} itens")
                extracted_items = [item.model_dump() for item in response.itens_extraidos]
            else:
                logger.warning(f"LLM não retornou nenhum item para: {licitacao.numero_pregao}")
        elif licitacao.itens:
            logger.warning(f"Nenhum texto de documento disponível. Utilizando o campo 'itens' completo na LLM.")
            raw_items_text = "\n".join(licitacao.itens)
            response = llm_service.extract_items(
                parsed_text=raw_items_text,
                scaffold=""
            )
            if response:
                extracted_items = [item.model_dump() for item in response.itens_extraidos]
        else:
            logger.warning(f"Nenhum texto processado e nenhuma base de itens para: {licitacao.numero_pregao}")

        licitacao_output = LicitacaoOutput(
            arquivo_json=licitacao.arquivo_json,
            numero_pregao=licitacao.numero_pregao,
            orgao=licitacao.orgao,
            cidade=licitacao.cidade,
            estado=licitacao.estado,
            anexos_processados=processed_files,
            itens_extraidos=[Item(**i) for i in extracted_items]
        )
        
        final_result.append(licitacao_output.model_dump())
    
    duration = time.time() - start_time
    
    logger.info("+" * 50)
    logger.info(f"Processamento concluido em: {duration / 60:.2f} minutos")
    FileManager.write_final_result(final_result)
    
if __name__ == "__main__":
    main()
