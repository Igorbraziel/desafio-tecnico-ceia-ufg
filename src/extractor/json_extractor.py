import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from src.utils.file_utils import FileManager
from src.utils.logging_utils import LoggingService
from src.models.schemas import LicitacaoInput, Anexo

logger = LoggingService.get_logger("extractor.json")

class JsonReader:
    """Classe responsável pela leitura e processamento dos arquivos JSON."""
    @staticmethod
    def extract_downloads_info(downloads_dir: Path) -> List[LicitacaoInput]:
        """Extrai informações dos arquivos JSON na pasta de downloads e retorna uma lista de objetos LicitacaoInput."""
        licitacao_list = []
        for file_path in downloads_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                        # 1. Carregar o conteúdo do arquivo JSON
                        raw_json = json.load(f)
                        data = raw_json["data"]

                        # 2. Extrair o nome do arquivo e criar a pasta de anexos correspondente
                        file_name = FileManager.get_file_name(file_path)
                        anexos_folder = downloads_dir / file_name

                        # 3. Criar lista de Anexos
                        anexos = [
                            Anexo(
                                nome=anexo["nome"],
                                formato=anexo["formato"],
                                url=anexo["url"],
                                caminho=anexo["caminho"],
                                hash_content=anexo["hash_content"],
                            ) for anexo in data.get("anexos", [])
                        ]


                        licitacao_input = LicitacaoInput(
                            arquivo_json=file_path,
                            numero_pregao=data["numero_pregao"],
                            objeto=data["objeto"],
                            orgao=data["orgao"],
                            cidade=data["cidade"],
                            estado=data["estado"],
                            itens=data["itens"],
                            anexos=anexos,
                            pasta_anexos=anexos_folder
                        )
                        licitacao_list.append(licitacao_input)
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Erro ao processar o arquivo JSON '{file_path}': {e}")

        if not licitacao_list:
            logger.warning(f"Nenhum arquivo JSON processado com sucesso na pasta: {downloads_dir}")
            
        return licitacao_list