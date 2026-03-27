from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path

class Anexo(BaseModel):
    nome: str
    formato: str
    url: str
    caminho: str
    hash_content: str

class LicitacaoInput(BaseModel):
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

class Item(BaseModel):
    """Representa um item extraído de uma licitação."""
    lote: Optional[str | None] = Field(description='Grupo/lote ao qual o item pertence (ex: "G1" , "G2" , "1" , "2" ). Caso não haja agrupamento, deve ser null.')
    item: int = Field(description='Número sequencial do item (inteiro, começando em 1).')
    objeto: str = Field(description='Descrição completa do item, incluindo categoria e especificações técnicas.')
    quantidade: int = Field(description='Quantidade solicitada do item.')
    unidade_fornecimento: str = Field(description='Unidade de fornecimento (ex: "Unidade" , "Caixa 50,00 UN" , "Pacote 500,00 FL" )')

class LicitacaoOutput(BaseModel):
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