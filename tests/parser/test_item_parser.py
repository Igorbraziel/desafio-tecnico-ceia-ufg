"""Testes unitários para o ItemParser."""
from src.parser.item_parser import ItemParser

def test_parse_itens_field_standard_format() -> None:
    raw_itens = [
        "1 - Cadeira de Escritório\nCadeira ergonômica preta para escritório, com rodas.\nTratamento Diferenciado: Tipo I - Participação Exclusiva de ME/EPP\nQuantidade: 15\nValor Estimado: R$ 500,00\nUnidade de fornecimento: Unidade\n----------\n",
        "2 - Mesa de Computador\nMesa retangular em L.\nAplicabilidade Margem de Preferência: Não\nQuantidade: 5\nValor Estimado: R$ 400,00\nUnidade de fornecimento: Peça\n----------"
    ]
    
    parsed = ItemParser.parse_itens_field(raw_itens)
    
    assert len(parsed) == 2
    
    item1 = parsed[0]
    assert item1["item"] == 1
    assert item1["quantidade"] == 15
    assert item1["unidade_fornecimento"] == "Unidade"
    assert "Cadeira de Escritório" in item1["objeto"]
    # Garante que as palavras cortadas sumiram da descricao principal
    assert "Tratamento Diferenciado" not in item1["objeto"]
    
    item2 = parsed[1]
    assert item2["item"] == 2
    assert item2["quantidade"] == 5
    assert item2["unidade_fornecimento"] == "Peça"
    assert "Mesa de Computador" in item2["objeto"]
    assert "Aplicabilidade" not in item2["objeto"]

def test_parse_itens_field_empty() -> None:
    assert ItemParser.parse_itens_field([]) == []
    assert ItemParser.parse_itens_field([""]) == []

def test_format_scaffold_for_prompt() -> None:
    parsed_items = [
        {"item": 1, "objeto": "Monitor 24 polegadas LED", "quantidade": 20, "unidade_fornecimento": "Unidade"},
        {"item": 2, "objeto": "Teclado USB", "quantidade": 30, "unidade_fornecimento": "Unidade"}
    ]
    
    scaffold = ItemParser.format_scaffold_for_prompt(parsed_items)
    
    assert "Total de itens esperados: 2" in scaffold
    assert "Item 1 | Nome: Monitor 24 polegadas LED | Qtd: 20" in scaffold
    assert "Item 2 | Nome: Teclado USB | Qtd: 30" in scaffold

def test_format_scaffold_truncates_long_names() -> None:
    long_name = "X" * 150
    parsed_items = [
        {"item": 1, "objeto": long_name, "quantidade": 1, "unidade_fornecimento": "Unidade"}
    ]
    
    scaffold = ItemParser.format_scaffold_for_prompt(parsed_items)
    
    expected_truncated = ("X" * 77) + "..."
    assert expected_truncated in scaffold
    assert len(expected_truncated) == 80

def test_format_scaffold_removes_duplicate_prefix() -> None:
    # Testa o name_pattern que retira strings repetidas do começo.
    parsed_items = [
        {"item": 1, "objeto": "NOTEBOOK NOTEBOOK DELL 16GB", "quantidade": 10, "unidade_fornecimento": "Unidade"}
    ]
    
    scaffold = ItemParser.format_scaffold_for_prompt(parsed_items)
    
    assert "Nome: NOTEBOOK NOTEBOOK DELL 16GB" not in scaffold
    assert "Nome: NOTEBOOK" in scaffold
