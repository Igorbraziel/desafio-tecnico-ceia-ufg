import argparse
import sys
from pathlib import Path
from src.utils.file_utils import FileManager
from pprint import pprint

def main():
    parser = argparse.ArgumentParser(description="Extração Estruturada de Itens de Licitações")
    parser.add_argument("--data-path", type=str, default="downloads/", help="Caminho para a pasta downloads/")
    
    args = parser.parse_args()
    
    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"Erro: Pasta '{data_path}' não encontrada.")
        sys.exit(1)
        
    print(f"Iniciando processamento em: {data_path}")

    info_list = FileManager.extract_info(data_path)


    
if __name__ == "__main__":
    main()
