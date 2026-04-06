# Extração Estruturada de Itens de Licitações Públicas

Este projeto automatiza a extração de itens de licitações públicas a partir de arquivos JSON e seus anexos (PDF, DOCX, XLS, DOC, ODT, ZIP).

## 🚀 Como Executar

1.  **Instale as dependências do sistema**:
    
    Este projeto requer utilitários para a extração de texto de arquivos legados e processamento de PDFs (OCR e imagens). No Ubuntu/Debian, instale:
    ```bash
    sudo apt-get update
    sudo apt-get install -y antiword tesseract-ocr tesseract-ocr-por poppler-utils
    ```

2.  **Instale as dependências Python**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure a API Key**:
    ```bash
    cp .env.example .env
    # Edite o .env e configure sua OPENAI_API_KEY
    ```

4.  **Execute a extração**:
    ```bash
    python -m src.main --data-path downloads/
    ```

## 📁 Estrutura do Projeto

- `src/`: Código-fonte principal.
    - `extractor/`: Lógica para extração de texto de PDFs, DOCXs, DOCs, ODTs, planilhas e ZIPs.
    - `parser/`: Lógica para limpar, isolar seções e formatar texto.
    - `models/`: Definições de esquemas de dados (Pydantic).
    - `services/`: Serviço de integração com LLM (GPT-4.1 Mini).
    - `utils/`: Utilitários de arquivo e logging.
- `tests/`: Testes unitários e de avaliação.
- `downloads/`: Pasta contendo o dataset (ignorada pelo Git).
- `results/`: Pasta com os resultados gerados.

## 🛠️ Abordagem Técnica

- **Seleção Inteligente de Documentos**: O `DocumentSelector` prioriza documentos de alta relevância (edital, termo de referência, relação de itens). Quando encontrados, apenas esses são processados — os demais são ignorados para reduzir ruído no contexto da LLM.
- **Extração de Texto**: PyMuPDF + pdfplumber (com tabelas) para PDFs, python-docx para DOCX, antiword para DOC, pandas para planilhas (XLS/XLSX/ODS), e extração recursiva de ZIPs.
- **Isolamento de Seção**: Cada documento tem sua seção de itens isolada individualmente via regex, removendo texto jurídico e boilerplate antes de enviar à LLM.
- **Scaffold Mínimo**: O campo `itens` do JSON é processado para gerar apenas uma referência de contagem (número do item + quantidade), forçando a LLM a extrair descrições completas dos documentos.
- **LLM (GPT-4.1 Mini)**: Contexto de ~1M tokens permite processar documentos longos em chamada única. Sistema de chunking como fallback para documentos excepcionalmente grandes.
- **Robustez**: Tratamento de erros para arquivos corrompidos (0 bytes), ausentes, com extensão incorreta, ou com formatação inesperada. OCR via Tesseract como último recurso para PDFs escaneados.

## 📊 Avaliação

```bash
# Avaliação contra gabarito
PYTHONPATH=. python tests/test_gabarito_amostra.py

# Auditoria estrutural
PYTHONPATH=. python tests/test_auditoria.py
```

## ⚠️ Limitações Conhecidas

- PDFs escaneados dependem de OCR (Tesseract), cuja precisão pode variar.
- Documentos com layouts muito atípicos podem dificultar o isolamento de seção.
- O scaffold fallback (quando não há anexos) tem qualidade limitada — depende do campo `itens` do JSON, que contém apenas descrições resumidas.

## 📄 Entrega

O resultado final é gerado no arquivo `results/resultado.json` seguindo o formato definido em `schema_saida.json`.
