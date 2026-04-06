import pytest
from src.parser.text_parser import TextParser

class TestTextParser:
    
    def test_chunk_text_short(self):
        """Testa o chunking com texto menor que o chunk_size."""
        text = "Hello world"
        chunks = TextParser.chunk_text(text, chunk_size=20, overlap=5)
        assert len(chunks) == 1
        assert chunks[0] == "Hello world"

    def test_chunk_text_long(self):
        """Testa o chunking com texto longo, verificando overlap e limites de parágrafo."""
        # Cria um texto com dois parágrafos explícitos
        part1 = "Parágrafo 1 de tamanho razoável para teste."
        part2 = "Parágrafo 2 com mais informações para completar."
        text = f"{part1}\n\n{part2}"
        
        # Tamanho do chunk forçado a cortar no meio do texto, perto do \n\n
        # part1 tem ~43 chars.
        chunks = TextParser.chunk_text(text, chunk_size=50, overlap=10)
        
        # O paragraph break está em 43. O chunk_size é 50.
        # Assim end inicial = 50. text.rfind("\n\n") encontra o break em 43 (que é > start=0).
        # Então o primeiro chunk vai de 0 a 43.
        assert len(chunks) >= 2
        assert chunks[0] == part1
        
    def test_chunk_text_no_paragraph(self):
        """Testa chunking em texto longo sem quebras de parágrafo completas."""
        text = "a" * 100
        chunks = TextParser.chunk_text(text, chunk_size=40, overlap=10)
        assert chunks[0] == "a" * 40
        assert chunks[1] == "a" * 40  # Start = 30 -> 30:70
        assert chunks[2] == "a" * 40  # Start = 60 -> 60:100
        assert len(chunks) == 3

    def test_clean_raw_text_empty(self):
        """Testa limpeza de string vazia."""
        assert TextParser.clean_raw_text("") == ""
        assert TextParser.clean_raw_text(None) == ""

    def test_clean_raw_text_control_chars(self):
        """Testa remoção de caracteres de controle."""
        text = "Texto\x00com\x0bcontrole\x1f"
        assert TextParser.clean_raw_text(text) == "Textocomcontrole"

    def test_clean_raw_text_repeating_dots(self):
        """Testa redução de pontos repetidos."""
        text = "Aguarde........ mais um pouco."
        assert TextParser.clean_raw_text(text) == "Aguarde... mais um pouco."

    def test_clean_raw_text_whitespace(self):
        """Testa remoção de espaços horizontais excessivos."""
        text = "Muito    espaço \t aqui."
        assert TextParser.clean_raw_text(text) == "Muito espaço aqui."

    def test_clean_raw_text_newlines(self):
        """Testa normalização de quebras de linha."""
        text = "Linha 1\r\nLinha 2\n\n\n\nLinha 3"
        cleaned = TextParser.clean_raw_text(text)
        assert cleaned == "Linha 1\nLinha 2\n\nLinha 3"

    def test_clean_raw_text_hyphenation(self):
        """Testa conserto de palavras separadas com hífen no fim da linha."""
        text = "Uma pala-\nvra hifenizada."
        assert TextParser.clean_raw_text(text) == "Uma palavra hifenizada."

    def test_clean_raw_text_punctuation_spacing(self):
        """Testa o ajuste de espaços ao redor de pontuações."""
        # Remove espaço antes, adiciona depois (se não for dígito e não tiver espaço)
        text = "Cadeira ,mesa . porta:10.5 e fim ;"
        cleaned = TextParser.clean_raw_text(text)
        assert "Cadeira, mesa. porta:10.5 e fim;" in cleaned

    def test_clean_raw_text_line_trimming(self):
        """Testa remoção de espaços no início e fim das linhas."""
        text = "   Linha com espaço no início  \nE no fim    \n  "
        cleaned = TextParser.clean_raw_text(text)
        assert cleaned == "Linha com espaço no início\nE no fim"

    def test_isolate_items_section_short_text(self):
        """Se o texto tiver menos de 2000 caracteres, deve retornar sem modificações."""
        short_text = "Um texto bem curto."
        assert TextParser.isolate_items_section(short_text) == short_text

    def test_isolate_items_section_no_anchors(self):
        """Texto maior que 2000 chars sem nenhuma âncora retorna o texto."""
        text = "A" * 2500
        assert TextParser.isolate_items_section(text) == text

    def test_isolate_items_section_cuts_start(self):
        """Verifica se encontra uma âncora de início válida e corta o arquivo antes dela."""
        prefix = "Lixo no início " * 100  # Tem mais de 100 caracteres antes
        anchor = "1 - Itens da Licitação "
        suffix = "Conteúdo relevante " * 100  # Para garantir tamanho > 2000
        
        full_text = prefix + anchor + suffix
        # Estender até > 2000 chars
        full_text += "B" * (2000 - len(full_text) + 10)
        
        result = TextParser.isolate_items_section(full_text)
        
        # O text_parser corta max(0, start_match.start() - 100)
        # O prefixo será cortado. O prefixo é bem grande.
        assert anchor in result
        assert len(result) < len(full_text)
        
    def test_isolate_items_section_preserves_groups(self):
        """Verifica se o parser consegue estender o corte caso ache Grupos após a âncora de finalização."""
        content = "Conteúdo anterior... " * 100  # Muito texto
        stop_anchor = "\nDas obrigações da contratada\n"
        group_section = "\nRelação de Grupos da Licitação:\nGrupo 1 - \nLixo após grupo 1..."
        
        # Precisa ter mais de 2000 caracteres para ser processado
        full_text = content + stop_anchor + group_section + ("Y" * 2000)
        
        result = TextParser.isolate_items_section(full_text)
        
        assert stop_anchor.strip() in result
        assert "Relação de Grupos da Licitação" in result
        assert "Grupo 1" in result

    def test_generic_numbered_paragraph_not_matched(self):
        """Verifica que '1. DO OBJETO' ou '1. DISPOSIÇÕES' NÃO é usado como âncora de início.
        
        O antigo padrão (?:^|\\n)\\s*(?:item\\s+)?1\\s*[-–.]\\s*\\w matchava esses
        parágrafos genéricos no início de editais, causando 99% de perda de conteúdo.
        """
        # Simula um edital: 1. DO OBJETO no início, itens descritos MUITO depois
        header = "EDITAL DE PREGÃO ELETRÔNICO N° 90038/2024\n\n"
        section1 = "1. DO OBJETO\nAquisição de material.\n\n"
        section2 = "2. DOS RECURSOS\nOs recursos serão interpostos...\n\n"
        items_section = "RELAÇÃO DE ITENS\nItem 1 - Computador - 10 UN\nItem 2 - Monitor - 20 UN\n"
        filler = "X" * 2000
        
        full_text = header + section1 + section2 + filler + items_section + filler
        
        result = TextParser.isolate_items_section(full_text)
        
        # Must find the items section, not cut at "1. DO OBJETO"
        assert "RELAÇÃO DE ITENS" in result
        assert "Item 1 - Computador" in result
        assert "Item 2 - Monitor" in result

    def test_minimum_content_guard(self):
        """Se o isolamento produz < 1500 chars de um documento > 10K, retorna texto completo."""
        # Cria um start anchor muito cedo seguido por um stop anchor logo depois
        filler_before = "A" * 5000
        start = "\nRelação de itens\n"
        tiny_content = "Algum conteúdo " * 10  # ~150 chars
        stop = "\nDas obrigações da contratada\n"
        filler_after = "B" * 10000
        
        full_text = filler_before + start + tiny_content + stop + filler_after
        
        result = TextParser.isolate_items_section(full_text)
        
        # Isolated text would be ~350 chars from a 15K+ doc → guard kicks in
        # Result should be the full text (truncated at 200K)
        assert len(result) > 5000  # Should NOT be the tiny isolated snippet

    def test_close_proximity_stop_anchor_skipped(self):
        """Se o stop anchor está a < 500 chars do início, busca o próximo."""
        filler = "Z" * 3000
        start = "\nRelação de itens\n"
        # First stop anchor right after start (column header, not a section)
        first_stop = "\nDas sanções\n"
        content = "Item 1 - Café - 50 UN\nItem 2 - Açúcar - 30 UN\n" * 30
        # Second stop anchor far away (this is the real one)
        second_stop = "\nDa habilitação\n"
        tail = "C" * 2000
        
        full_text = filler + start + first_stop + content + second_stop + tail
        
        result = TextParser.isolate_items_section(full_text)
        
        # Should skip the first "das sanções" (too close) and use "da habilitação"
        assert "Item 1 - Café" in result
        assert "Item 2 - Açúcar" in result

    def test_local_de_entrega_not_a_stop_anchor(self):
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
