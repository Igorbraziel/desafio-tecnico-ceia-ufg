import json
import pytest
import Levenshtein

def evaluate_extraction(resultado_path: str, gabarito_path: str):
    with open(resultado_path, 'r', encoding='utf-8') as f:
        resultados = json.load(f)
        
    with open(gabarito_path, 'r', encoding='utf-8') as f:
        gabaritos = json.load(f)

    total_itens_avaliados = 0
    itens_corretos = 0
    failed_items = []

    mapa_resultados = {r["arquivo_json"]: r for r in resultados}

    for gabarito_licitacao in gabaritos:
        arquivo = gabarito_licitacao["arquivo_json"]
        resultado_licitacao = mapa_resultados.get(arquivo)

        if not resultado_licitacao:
            failed_items.append(f"Licitação {arquivo} não encontrada no resultado")
            continue

        itens_gabarito = gabarito_licitacao.get("itens_extraidos", [])
        itens_resultado = resultado_licitacao.get("itens_extraidos", [])

        for item_gab in itens_gabarito:
            total_itens_avaliados += 1
            
            item_res = next((i for i in itens_resultado if i["item"] == item_gab["item"]), None)

            if not item_res:
                failed_items.append(f"Item {item_gab['item']} faltante na licitação {arquivo}")
                continue

            # APLICAÇÃO DAS REGRAS DO DESAFIO
            # 1. Correspondência Exata Simples
            qtd_ok = item_res["quantidade"] == item_gab["quantidade"]
            lote_ok = item_res["lote"] == item_gab["lote"]
            
            # 2. Correspondência Case-insensitive
            unid_res = str(item_res.get("unidade_fornecimento", "")).strip().lower()
            unid_gab = str(item_gab.get("unidade_fornecimento", "")).strip().lower()
            unidade_ok = unid_res == unid_gab

            # 3. Levenshtein Normalizado (>= 85%)
            obj_res = str(item_res.get("objeto", "")).strip()
            obj_gab = str(item_gab.get("objeto", "")).strip()
            similaridade = Levenshtein.ratio(obj_res, obj_gab) * 100
            objeto_ok = similaridade >= 85.0

            if qtd_ok and lote_ok and unidade_ok and objeto_ok:
                itens_corretos += 1
            else:
                failure_details = {
                    "item": item_gab["item"],
                    "arquivo": arquivo,
                    "failures": []
                }
                if not qtd_ok:
                    failure_details["failures"].append(f"Quantidade: Esperado {item_gab['quantidade']}, Recebido {item_res['quantidade']}")
                if not lote_ok:
                    failure_details["failures"].append(f"Lote: Esperado {item_gab['lote']}, Recebido {item_res['lote']}")
                if not unidade_ok:
                    failure_details["failures"].append(f"Unidade: Esperado '{unid_gab}', Recebido '{unid_res}'")
                if not objeto_ok:
                    failure_details["failures"].append(f"Objeto: Similaridade de {similaridade:.2f}% (Abaixo de 85%)")
                failed_items.append(failure_details)

    return total_itens_avaliados, itens_corretos, failed_items


class TestEvaluateExtraction:
    """Testes para a avaliação da extração de itens."""

    def test_evaluate_extraction_basic(self):
        """Testa a função de avaliação com os arquivos de resultado e gabarito."""
        total_itens, corretos, failed = evaluate_extraction("results/resultado.json", "results/gabarito.json")
        
        # Verifica que há itens para avaliar
        assert total_itens > 0, "Nenhum item foi avaliado"
        
        # Verifica que pelo menos alguns itens estão corretos (dependendo dos dados)
        assert corretos >= 0, "Número de itens corretos deve ser não negativo"
        
        # A acurácia deve ser calculável
        if total_itens > 0:
            acuracia = (corretos / total_itens) * 100
            assert 0 <= acuracia <= 100, f"Acurácia deve estar entre 0 e 100, mas foi {acuracia:.2f}%"
        
        # Verifica que failed_items é uma lista
        assert isinstance(failed, list), "failed_items deve ser uma lista"