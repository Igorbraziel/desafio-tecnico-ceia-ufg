"""Testes unitários para a lógica de LlmService."""
from src.services.llm_service import LlmService
from src.models.schemas import Item

def make_item(item_num: int, objeto: str, quantidade: int = 1,
              lote: str | None = None, unidade: str = "Unidade") -> Item:
    """Helper para criar itens de teste."""
    return Item(
        lote=lote,
        item=item_num,
        objeto=objeto,
        quantidade=quantidade,
        unidade_fornecimento=unidade,
    )


class TestDeduplicateItems:
    """Testes para LlmService._deduplicate_items()"""

    def setup_method(self) -> None:
        self.service = LlmService.__new__(LlmService)

    def test_empty_list(self) -> None:
        result = self.service._deduplicate_items([])
        assert result == []

    def test_no_duplicates(self) -> None:
        items = [
            make_item(1, "AMPLIFICADOR PARA BAIXO 150W RMS"),
            make_item(2, "BATERIA ACÚSTICA ONIX SKINNY 20"),
            make_item(3, "CABO MICROFONE 2X0,30 BALANCEADO"),
        ]
        result = self.service._deduplicate_items(items)
        assert len(result) == 3

    def test_exact_duplicates(self) -> None:
        items = [
            make_item(1, "AMPLIFICADOR PARA BAIXO 150W RMS"),
            make_item(1, "AMPLIFICADOR PARA BAIXO 150W RMS"),
        ]
        result = self.service._deduplicate_items(items)
        assert len(result) == 1

    def test_real_world_chunk_duplication(self) -> None:
        """Simula o cenário real: mesmo item aparecendo em 2 chunks."""
        items = [
            # Chunk 1 output
            make_item(3, "Planejamento, Orçamento, Contabilidade Pública e Tesouraria", 12),
            make_item(4, "Gestão de pessoas contendo os módulos: folha de pagamento e e-social", 12),
            # Chunk 2 output
            make_item(3, "Planejamento, Orçamento, Contabilidade Pública e Tesouraria", 12),
            make_item(4, "Gestão de pessoas contendo os módulos: folha de pagamento e e-social", 12),
        ]
        result = self.service._deduplicate_items(items)
        assert len(result) == 2

    def test_sorted_output(self) -> None:
        items = [
            make_item(3, "Terceiro item"),
            make_item(1, "Primeiro item"),
            make_item(2, "Segundo item"),
        ]
        result = self.service._deduplicate_items(items)
        assert [r.item for r in result] == [1, 2, 3]

class TestGetExpectedCount:
    """Testes para LlmService._get_expected_count()"""
    def test_with_count(self) -> None:
        scaffold = "Total de itens esperados: 47\nItem 1 | Nome: AMPLIFICADOR | Qtd: 1"
        assert LlmService._get_expected_count(scaffold) == 47

    def test_without_count(self) -> None:
        assert LlmService._get_expected_count("") is None

    def test_no_scaffold(self) -> None:
        assert LlmService._get_expected_count("some random text") is None


class TestBuildUserPromptChunkContext:
    """Verifica que o contexto de chunk aparece no prompt."""

    def setup_method(self) -> None:
        self.service = LlmService.__new__(LlmService)

    def test_single_chunk_no_context(self) -> None:
        prompt = self.service._build_user_prompt("text", total_chunks=1)
        assert "trecho" not in prompt

    def test_multi_chunk_has_context(self) -> None:
        prompt = self.service._build_user_prompt("text", chunk_index=1, total_chunks=2)
        assert "trecho 1/2" in prompt
        assert "SOMENTE" in prompt
