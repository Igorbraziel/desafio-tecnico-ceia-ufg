from pathlib import Path
from unittest.mock import patch
from src.extractor.document_selector import DocumentSelector

def test_ignored_documents_filtered_out(tmp_path):
    # Criar arquivos que devem ser ignorados
    (tmp_path / "contrato.pdf").touch()
    (tmp_path / "planilha_custos.xlsx").touch()
    (tmp_path / "ata_registro_precos.pdf").touch()

    docs = DocumentSelector.select_best_documents(tmp_path)
    assert len(docs) == 0

def test_priority_documents_selected(tmp_path):
    # Criar um arquivo prioritário e arquivos de fallback
    (tmp_path / "edital_123.pdf").touch()
    (tmp_path / "anexo_secundario.pdf").touch()
    (tmp_path / "documento_qualquer.pdf").touch()

    docs = DocumentSelector.select_best_documents(tmp_path)
    
    # Apenas o arquivo prioritário deve ser selecionado
    assert len(docs) == 1
    assert "edital" in docs[0].name.lower()

def test_multiple_priority_documents_sorting(tmp_path):
    # Criar vários arquivos prioritários
    (tmp_path / "edital_123.pdf").touch()
    (tmp_path / "termo_referencia.pdf").touch()

    docs = DocumentSelector.select_best_documents(tmp_path)
    
    assert len(docs) == 2
    assert "termo_referencia" in docs[0].name.lower()
    assert "edital" in docs[1].name.lower()

def test_fallback_documents_selected_when_no_priority(tmp_path):
    # Nenhum arquivo prioritario nem ignorado, apenas fallback
    (tmp_path / "anexo_1.pdf").touch()
    (tmp_path / "anexo_2.pdf").touch()

    docs = DocumentSelector.select_best_documents(tmp_path)
    
    # Ambos os arquivos válidos precisam ser retornados como fallback
    assert len(docs) == 2

@patch('src.extractor.document_selector.FileManager.verify_file_exists')
def test_ignore_missing_files(mock_verify_exists, tmp_path):
    mock_verify_exists.return_value = False
    
    # Cria o arquivo para iterdir() pegar, mas o FileManager dirá que não existe
    (tmp_path / "edital.pdf").touch()
    
    docs = DocumentSelector.select_best_documents(tmp_path)
    assert len(docs) == 0
