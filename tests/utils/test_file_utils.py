"""Testes unitários para utilitários de arquivo."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.utils.file_utils import FileManager

def test_clean_filename() -> None:
    original = "2024-08-15-conlicitacao-164dd14eb625bb75bf0566e11d2ceca8-edital_final.pdf"
    cleaned = FileManager.clean_filename(original)
    assert cleaned == "edital_final.pdf"

def test_clean_filename_no_match() -> None:
    original = "apenas_outro_arquivo_sem_prefixo.pdf"
    cleaned = FileManager.clean_filename(original)
    assert cleaned == original

@patch('src.utils.file_utils.filetype.guess')
def test_guess_file_extension_success(mock_guess: MagicMock) -> None:
    mock_kind = MagicMock()
    mock_kind.extension = "pdf"
    mock_guess.return_value = mock_kind
    
    ext = FileManager.guess_file_extension(Path("dummy_file_without_ext"))
    assert ext == ".pdf"
    mock_guess.assert_called_once()

@patch('src.utils.file_utils.filetype.guess')
def test_guess_file_extension_none(mock_guess: MagicMock) -> None:
    mock_guess.return_value = None
    
    ext = FileManager.guess_file_extension(Path("dummy_file"))
    assert ext == ""

def test_get_file_name_and_extension() -> None:
    """Testa a extração de nome e extensão de um caminho."""
    path = Path("/home/user/documentos/edital.docx")
    assert FileManager.get_file_name(path) == "edital"
    assert FileManager.get_file_extension(path) == ".docx"

def test_verify_file_exists(tmp_path: Path) -> None:
    """Testa a verificação de existência de arquivo."""
    file_path = tmp_path / "teste.txt"
    assert not FileManager.verify_file_exists(file_path)
    
    file_path.touch()
    assert FileManager.verify_file_exists(file_path)

def test_verify_file_has_content(tmp_path: Path) -> None:
    """Testa a verificação de conteúdo em arquivo."""
    file_path = tmp_path / "vazio.txt"
    file_path.touch()
    assert not FileManager.verify_file_has_content(file_path)
    
    file_path.write_text("Conteudo")
    assert FileManager.verify_file_has_content(file_path)
