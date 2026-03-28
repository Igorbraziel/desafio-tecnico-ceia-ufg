import argparse
import sys
import time
from pathlib import Path

from src.utils.logging_utils import LoggingService
from src.utils.file_utils import FileManager
from src.extractor.json_extractor import JsonReader
from src.extractor.attachment_reader import AttachmentReader
from src.models.schemas import LicitacaoOutput
from src.services.llm_service import LlmService

def main():
    # Inicializa a configuração de Logging
    logger = LoggingService.setup_logging()
    final_result = []
    llm_service = LlmService()
    
    parser = argparse.ArgumentParser(description="Extração Estruturada de Itens de Licitações")
    parser.add_argument("--data-path", type=str, default="downloads/", help="Caminho para a pasta downloads/")
    
    args = parser.parse_args()
    
    data_path = Path(args.data_path)
    if not data_path.exists():
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

    for licitacao in licitacao_list:
        logger.info(f"Processando licitação: {licitacao.numero_pregao}")

        full_processed_text, processed_files = AttachmentReader.read_attachment(licitacao.pasta_anexos)

        logger.info(f"Texto extraído para licitação (total de {len(full_processed_text)} caracteres):\n")
        logger.info(f"Numero de arquivos processados para licitação: {len(processed_files)}")
        
        extracted_items = []
        
        if full_processed_text:
            parsed_response = llm_service.extract_items(parsed_text=full_processed_text)
            
            if parsed_response:
                logger.info(f"Itens de licitação extraidos com sucesso para a licitação: {licitacao.numero_pregao}")
                extracted_items = [item.model_dump() for item in parsed_response.itens_extraidos]
            else:
                logger.warning(f"LLM não retornou nenhum item para a licitação: {licitacao.numero_pregao}")
        else:
            logger.warning(f"Nenhum texto processado para a licitação: {licitacao.numero_pregao}")

        licitacao_output = LicitacaoOutput(
            arquivo_json=licitacao.arquivo_json,
            numero_pregao=licitacao.numero_pregao,
            orgao=licitacao.orgao,
            cidade=licitacao.cidade,
            estado=licitacao.estado,
            anexos_processados=processed_files,
            itens_extraidos=extracted_items
        )
        
        final_result.append(licitacao_output.model_dump())
    
    duration = time.time() - start_time
    
    logger.info("+" * 50)
    logger.info(f"Processamento concluido em: {duration:.2f} segundos")
    FileManager.write_final_result(final_result)
    
if __name__ == "__main__":
    main()
