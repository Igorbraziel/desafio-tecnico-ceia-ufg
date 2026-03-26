from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path

@dataclass
class Anexo:
    nome: str
    formato: str
    url: str
    caminho: str
    hash_content: str

@dataclass
class LicitacaoInput:
    """Representa os dados brutos lidos do JSON de entrada."""
    arquivo_json:  str
    numero_pregao: str
    objeto:        str
    orgao:         str
    cidade:        str
    estado:        str
    itens:         List[str]
    anexos:        List[Anexo]
    pasta_anexos:  Path

@dataclass
class Item:
    """Representa um item extraído de uma licitação."""
    item:                 int
    objeto:               str
    quantidade:           int
    unidade_fornecimento: str
    lote:                 Optional[str | int] = None

@dataclass
class LicitacaoOutput:
    """Representa o resultado final de uma licitação processada."""
    arquivo_json:       str
    numero_pregao:      str
    orgao:              str
    cidade:             str
    estado:             str
    anexos_processados: List[str]
    itens_extraidos:    List[Item]

    def to_dict(self) -> dict:
        return {
            "arquivo_json":       self.arquivo_json,
            "numero_pregao":      self.numero_pregao,
            "orgao":              self.orgao,
            "cidade":             self.cidade,
            "estado":             self.estado,
            "anexos_processados": self.anexos_processados,
            "itens_extraidos": [
                {
                    "lote":                 i.lote,
                    "item":                 i.item,
                    "objeto":               i.objeto,
                    "quantidade":           i.quantidade,
                    "unidade_fornecimento": i.unidade_fornecimento,
                }
                for i in self.itens_extraidos
            ],
        }