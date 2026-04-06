"""Testes unitários para a classe TextParser."""
from src.parser.text_parser import TextParser

class TestTextParser:
    
    def test_chunk_text_short(self) -> None:
        """Testa o chunking com texto menor que o chunk_size."""
        text = "Hello world"
        chunks = TextParser.chunk_text(text, chunk_size=20, overlap=5)
        assert len(chunks) == 1
        assert chunks[0] == "Hello world"

    def test_chunk_text_long(self) -> None:
        """Testa o chunking com texto longo, verificando overlap e limites de parágrafo."""
        part1 = "Parágrafo 1 de tamanho razoável para teste."
        part2 = "Parágrafo 2 com mais informações para completar."
        text = f"{part1}\n\n{part2}"
        
        chunks = TextParser.chunk_text(text, chunk_size=50, overlap=10)
        
        assert len(chunks) >= 2
        assert chunks[0] == part1
        
    def test_chunk_text_no_paragraph(self) -> None:
        """Testa chunking em texto longo sem quebras de parágrafo completas."""
        text = "a" * 100
        chunks = TextParser.chunk_text(text, chunk_size=40, overlap=10)
        assert chunks[0] == "a" * 40
        assert chunks[1] == "a" * 40
        assert chunks[2] == "a" * 40 
        assert len(chunks) == 3

    def test_clean_raw_text_empty(self) -> None:
        """Testa limpeza de string vazia."""
        assert TextParser.clean_raw_text("") == ""
        assert TextParser.clean_raw_text(None) == ""  # type: ignore

    def test_clean_raw_text_control_chars(self) -> None:
        """Testa remoção de caracteres de controle."""
        text = "Texto\x00com\x0bcontrole\x1f"
        assert TextParser.clean_raw_text(text) == "Textocomcontrole"

    def test_clean_raw_text_repeating_dots(self) -> None:
        """Testa redução de pontos repetidos."""
        text = "Aguarde........ mais um pouco."
        assert TextParser.clean_raw_text(text) == "Aguarde... mais um pouco."

    def test_clean_raw_text_whitespace(self) -> None:
        """Testa remoção de espaços horizontais excessivos."""
        text = "Muito    espaço \t aqui."
        assert TextParser.clean_raw_text(text) == "Muito espaço aqui."

    def test_clean_raw_text_newlines(self) -> None:
        """Testa normalização de quebras de linha."""
        text = "Linha 1\r\nLinha 2\n\n\n\nLinha 3"
        cleaned = TextParser.clean_raw_text(text)
        assert cleaned == "Linha 1\nLinha 2\n\nLinha 3"

    def test_clean_raw_text_hyphenation(self) -> None:
        """Testa conserto de palavras separadas com hífen no fim da linha."""
        text = "Uma pala-\nvra hifenizada."
        assert TextParser.clean_raw_text(text) == "Uma palavra hifenizada."

    def test_clean_raw_text_punctuation_spacing(self) -> None:
        """Testa o ajuste de espaços ao redor de pontuações."""
        text = "Cadeira ,mesa . porta:10.5 e fim ;"
        cleaned = TextParser.clean_raw_text(text)
        assert "Cadeira, mesa. porta:10.5 e fim;" in cleaned

    def test_clean_raw_text_line_trimming(self) -> None:
        """Testa remoção de espaços no início e fim das linhas."""
        text = "   Linha com espaço no início  \nE no fim    \n  "
        cleaned = TextParser.clean_raw_text(text)
        assert cleaned == "Linha com espaço no início\nE no fim"

    def test_isolate_items_section_short_text(self) -> None:
        """Se o texto tiver menos de 2000 caracteres, deve retornar sem modificações."""
        short_text = "Um texto bem curto."
        assert TextParser.isolate_items_section(short_text) == short_text

    def test_isolate_items_section_no_anchors(self) -> None:
        """Texto maior que 2000 chars sem nenhuma âncora retorna o texto."""
        text = "A" * 2500
        assert TextParser.isolate_items_section(text) == text

    def test_isolate_items_section_cuts_start(self) -> None:
        """Verifica se encontra uma âncora de início válida e corta o arquivo antes dela."""
        prefix = "Lixo no início " * 100  
        anchor = "1 - Itens da Licitação "
        suffix = "Conteúdo relevante " * 100
        
        full_text = prefix + anchor + suffix
        full_text += "B" * (2000 - len(full_text) + 10)
        
        result = TextParser.isolate_items_section(full_text)
        
        assert anchor in result
        assert len(result) < len(full_text)
        
    def test_isolate_items_section_preserves_groups(self) -> None:
        """Verifica se o parser consegue estender o corte caso ache Grupos após a âncora de finalização."""
        content = "Conteúdo anterior... " * 100
        stop_anchor = "\nDas obrigações da contratada\n"
        group_section = "\nRelação de Grupos da Licitação:\nGrupo 1 - \nLixo após grupo 1..."
        
        full_text = content + stop_anchor + group_section + ("Y" * 2000)
        
        result = TextParser.isolate_items_section(full_text)
        
        assert stop_anchor.strip() in result
        assert "Relação de Grupos da Licitação" in result
        assert "Grupo 1" in result

    def test_generic_numbered_paragraph_not_matched(self) -> None:
        """Verifica que '1. DO OBJETO' ou '1. DISPOSIÇÕES' NÃO é usado como âncora de início.
        """
        header = "EDITAL DE PREGÃO ELETRÔNICO N° 90038/2024\n\n"
        section1 = "1. DO OBJETO\nAquisição de material.\n\n"
        section2 = "2. DOS RECURSOS\nOs recursos serão interpostos...\n\n"
        items_section = "RELAÇÃO DE ITENS\nItem 1 - Computador - 10 UN\nItem 2 - Monitor - 20 UN\n"
        filler = "X" * 2000
        
        full_text = header + section1 + section2 + filler + items_section + filler
        
        result = TextParser.isolate_items_section(full_text)
        
        assert "RELAÇÃO DE ITENS" in result
        assert "Item 1 - Computador" in result
        assert "Item 2 - Monitor" in result

    def test_minimum_content_guard(self) -> None:
        """Se o isolamento produz < 1500 chars de um documento > 10K, retorna texto completo."""
        filler_before = "A" * 5000
        start = "\nRelação de itens\n"
        tiny_content = "Algum conteúdo " * 10  
        stop = "\nDas obrigações da contratada\n"
        filler_after = "B" * 10000
        
        full_text = filler_before + start + tiny_content + stop + filler_after
        
        result = TextParser.isolate_items_section(full_text)
        
        assert len(result) > 5000

    def test_close_proximity_stop_anchor_skipped(self) -> None:
        """Se o stop anchor está a < 500 chars do início, busca o próximo."""
        filler = "Z" * 3000
        start = "\nRelação de itens\n"
        first_stop = "\nDas sanções\n"
        content = "Item 1 - Café - 50 UN\nItem 2 - Açúcar - 30 UN\n" * 30
        second_stop = "\nDa habilitação\n"
        tail = "C" * 2000
        
        full_text = filler + start + first_stop + content + second_stop + tail
        
        result = TextParser.isolate_items_section(full_text)
        
        assert "Item 1 - Café" in result
        assert "Item 2 - Açúcar" in result

    def test_local_de_entrega_not_a_stop_anchor(self) -> None:
        """'Local de Entrega' NÃO deve cortar o texto, pois aparece abaixo de cada item
        em documentos relacaoitens do Compras.gov.br."""
        header = "RELAÇÃO DE ITENS\n\n"
        item1 = "Item 1 - Notebook\nLocal de Entrega: Brasília\n\n"
        item2 = "Item 2 - Monitor\nLocal de Entrega: São Paulo\n\n"
        item3 = "Item 3 - Teclado\nLocal de Entrega: Rio de Janeiro\n\n"
        filler = "D" * 2000
        
        full_text = filler + header + item1 + item2 + item3 + filler
        
        result = TextParser.isolate_items_section(full_text)
        
        assert "Item 1 - Notebook" in result
        assert "Item 2 - Monitor" in result
        assert "Item 3 - Teclado" in result
