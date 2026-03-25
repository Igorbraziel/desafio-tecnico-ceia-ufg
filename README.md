# Extração Estruturada de Itens de Licitações Públicas

Este projeto automatiza a extração de itens de licitações públicas a partir de arquivos JSON e seus anexos (PDF/DOCX).

## 🚀 Como Executar

1.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Execute a extração**:
    ```bash
    python src/main.py --data-path downloads/
    ```

## 📁 Estrutura do Projeto

- `src/`: Código-fonte principal.
    - `extractor/`: Lógica para extração de texto de PDFs e DOCXs.
    - `parser/`: Lógica para identificar e estruturar os itens licitados.
    - `models/`: Definições de esquemas de dados (Pydantic).
- `tests/`: Testes unitários e de integração.
- `downloads/`: Pasta contendo o dataset (ignorada pelo Git).
- `results/`: Pasta com os resultados gerados.

## 🛠️ Abordagem Técnica

- **Extração de Texto**: Uso de `pypdf` para documentos estruturados e `python-docx` para o formato Microsoft Word.
- **Parsing**: Aplicação de expressões regulares e heurísticas para identificar lotes, itens, objetos e quantidades em textos complexos.
- **Robustez**: Tratamento de erros para arquivos corrompidos, ausentes ou com formatação inesperada.

## 📄 Entrega

O resultado final é gerado no arquivo `results/resultado.json` seguindo o formato definido em `schema_saida.json`.
