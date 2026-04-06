"""Definição de modelos de dados (Pydantic) para entrada e saída do sistema."""
from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path

class Anexo(BaseModel):
    """Representa um arquivo anexo associado a uma licitação."""

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
    itens_scaffold: str = ""  # Referência limpa dos itens do JSON, formatada para prompt LLM

class Item(BaseModel):
    """Representa um item extraído de uma licitação."""

    lote: Optional[str | None] = Field(description='Grupo/lote ao qual o item pertence (ex: "G1" , "G2" , "1" , "2" ). Caso não haja agrupamento, deve ser null.')
    item: int = Field(description='Número sequencial do item (inteiro).')
    objeto: str = Field(description='Descrição completa do item, incluindo categoria e especificações técnicas.')
    quantidade: int = Field(description='Quantidade solicitada do item.')
    unidade_fornecimento: str = Field(description='Unidade de fornecimento (ex: "Unidade" , "Caixa 50,00 UN" , "Pacote 500,00 FL" )')
    
class ItemList(BaseModel):
    """Representa a lista de itens extraídos de uma licitação."""

    itens_extraidos: List[Item]

class LicitacaoOutput(BaseModel):
    """Representa o resultado final de uma licitação processada."""

    arquivo_json:       str
    numero_pregao:      str
    orgao:              str
    cidade:             str
    estado:             str
    anexos_processados: List[str]
    itens_extraidos:    List[Item]