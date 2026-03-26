import argparse
import sys
import time
from pathlib import Path

from src.utils.logging_utils import LoggingService
from src.extractor.json_extractor import JsonReader
from src.extractor.attachment_reader import AttachmentReader

def main():
    # Inicializa a configuração de Logging
    logger = LoggingService.setup_logging()
    
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
        full_text, processed_files = AttachmentReader.read_attachment(licitacao.pasta_anexos)
        logger.info(f"Primeiros 500 caracteres do texto extraído para licitação (total de {len(full_text)} caracteres):\n{full_text[:500]}...")  # Log dos primeiros 500 caracteres do texto extraído
        logger.info(f"Numero de arquivos processados para licitação: {len(processed_files)}")

    duration = time.time() - start_time
    logger.info(f"Tempo total de processamento: {duration:.2f} segundos")
    
if __name__ == "__main__":
    main()
