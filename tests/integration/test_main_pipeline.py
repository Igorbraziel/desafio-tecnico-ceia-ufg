import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.main import main

@patch('src.main.JsonReader.extract_downloads_info')
@patch('src.main.AttachmentReader.read_attachment')
@patch('src.main.LlmService')
@patch('src.main.FileManager.write_final_result')
def test_main_pipeline_success(mock_write_final_result, mock_llm_service_class, mock_read_attachment, mock_extract_downloads, tmp_path):
    # Simula os argumentos de linha de comando
    test_args = ["main.py", "--data-path", str(tmp_path)]
    
    # Simula a estrutura de dados LicitacaoInfo extraida
    mock_licitacao = MagicMock()
    mock_licitacao.numero_pregao = "12/2024"
    mock_licitacao.pasta_anexos = Path("fake_path")
    mock_licitacao.itens_scaffold = "Item 1"
    mock_licitacao.arquivo_json = "process.json"
    mock_licitacao.orgao = "UFG"
    mock_licitacao.cidade = "Goiania"
    mock_licitacao.estado = "GO"
    
    mock_extract_downloads.return_value = [mock_licitacao]
    
    # Simula leitura de anexos com sucesso
    mock_read_attachment.return_value = ("Texto completo do Edital mock", ["edital.pdf"])
    
    # Simula a resposta do LLM
    mock_llm_instance = MagicMock()
    mock_parsed_response = MagicMock()
    
    # Criando mock para item de output para o `model_dump()` funcionar
    mock_item = MagicMock()
    mock_item.model_dump.return_value = {"item": 1, "objeto": "Mesa", "quantidade": 5, "unidade_fornecimento": "Unidade"}
    mock_parsed_response.itens_extraidos = [mock_item]
    
    mock_llm_instance.extract_items.return_value = mock_parsed_response
    mock_llm_service_class.return_value = mock_llm_instance
    
    with patch.object(sys, 'argv', test_args):
        main()
        
    # Verificacoes
    mock_extract_downloads.assert_called_once_with(tmp_path)
    mock_read_attachment.assert_called_once_with(Path("fake_path"))
    mock_llm_instance.extract_items.assert_called_once_with(
        parsed_text="Texto completo do Edital mock",
        scaffold="Item 1"
    )
    
    # O mock de gravacao deve ser chamado com um output iteravel
    mock_write_final_result.assert_called_once()
    saved_data = mock_write_final_result.call_args[0][0] # Primeiro argumento posicional
    assert len(saved_data) == 1
    assert saved_data[0]["numero_pregao"] == "12/2024"
    assert saved_data[0]["itens_extraidos"][0]["objeto"] == "Mesa"

@patch('src.main.JsonReader.extract_downloads_info')
@patch('src.main.LlmService')
def test_main_pipeline_data_path_not_found(mock_llm_service, mock_extract, caplog):
    test_args = ["main.py", "--data-path", "/dir_nao_existente_1234"]
    
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as excinfo:
            main()
            
    assert excinfo.value.code == 1
    # Verifica que ele parou antes de chamar o reader
    mock_extract.assert_not_called()
