import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import fitz
from src.extractor.pdf_extractor import PdfExtractor

@pytest.fixture
def mock_file_manager():
    with patch('src.extractor.pdf_extractor.FileManager') as mock:
        mock.verify_file_exists.return_value = True
        mock.verify_file_has_content.return_value = True
        yield mock

@patch('src.extractor.pdf_extractor.fitz.open')
def test_successful_pymupdf_extraction(mock_fitz_open, mock_file_manager):
    mock_doc = MagicMock()
    mock_doc.is_pdf = True
    mock_doc.page_count = 1
    
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Texto extraído com PyMuPDF"
    mock_doc.__iter__.return_value = [mock_page]
    
    mock_fitz_open.return_value = mock_doc

    with patch('src.extractor.pdf_extractor.PdfExtractor._extract_tables_with_pdfplumber') as mock_tables:
        mock_tables.return_value = ""
        text = PdfExtractor.extract_text_from_pdf(Path("dummy.pdf"))
    
    assert "Texto extraído com PyMuPDF" in text
    mock_fitz_open.assert_called()

@patch('src.extractor.pdf_extractor.fitz.open')
@patch('src.extractor.pdf_extractor.PdfExtractor._extract_with_pdfplumber_text')
def test_fallback_to_pdfplumber(mock_pdfplumber_text, mock_fitz_open, mock_file_manager):
    # fitz says PDF is valid but returns empty text (e.g. scanned image with no text layer)
    mock_doc = MagicMock()
    mock_doc.is_pdf = True
    mock_doc.page_count = 1
    
    mock_page = MagicMock()
    mock_page.get_text.return_value = "" # No text extracted
    mock_doc.__iter__.return_value = [mock_page]
    
    mock_fitz_open.return_value = mock_doc
    
    mock_pdfplumber_text.return_value = "Texto fallback pdfplumber"
    
    text = PdfExtractor.extract_text_from_pdf(Path("scanned.pdf"))
    
    assert text == "Texto fallback pdfplumber"
    mock_pdfplumber_text.assert_called_once()

@patch('src.extractor.pdf_extractor.fitz.open')
@patch('src.extractor.pdf_extractor.PdfExtractor._extract_with_pdfplumber_text')
@patch('src.extractor.pdf_extractor.PdfExtractor._extract_with_ocr')
def test_fallback_to_ocr(mock_ocr, mock_pdfplumber_text, mock_fitz_open, mock_file_manager):
    # Both fitz and pdfplumber return empty
    mock_doc = MagicMock()
    mock_doc.is_pdf = True
    mock_doc.page_count = 1
    mock_page = MagicMock()
    mock_page.get_text.return_value = ""
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc
    
    mock_pdfplumber_text.return_value = ""
    mock_ocr.return_value = "Texto extraído com OCR"
    
    text = PdfExtractor.extract_text_from_pdf(Path("heavy_scanned.pdf"))
    
    assert text == "Texto extraído com OCR"
    mock_ocr.assert_called_once()

@patch('src.extractor.pdf_extractor.fitz.open')
def test_file_data_error_aborts(mock_fitz_open, mock_file_manager):
    # Verifica validacao inicial estrutural de pdf broken
    # fitz throws on first attempt
    mock_fitz_open.side_effect = fitz.FileDataError("Corrupted")
    
    with patch('src.extractor.pdf_extractor.PdfExtractor._extract_with_pdfplumber_text') as mock_plumber:
        text = PdfExtractor.extract_text_from_pdf(Path("broken.pdf"))
        
        # Must abort fallback and return empty
        assert text == ""
        mock_plumber.assert_not_called()
