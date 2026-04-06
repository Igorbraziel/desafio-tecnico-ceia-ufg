# Extração Estruturada de Itens de Licitações Públicas

Este projeto automatiza a extração estruturada de itens de licitações públicas a partir de arquivos JSON e seus anexos (PDF, DOCX, XLS, DOC, ODT, ZIP), utilizando técnicas avançadas de processamento de documentos e inteligência artificial.

## Sumário

- [Descrição](#descrição)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Abordagem Técnica](#abordagem-técnica)
- [Avaliação](#avaliação)
- [Limitações](#limitações)
- [Saída](#saída)

## Descrição

O sistema processa dados de licitações públicas, extraindo itens estruturados de documentos anexos. Utiliza seleção inteligente de documentos, extração de texto robusta e integração com modelos de linguagem para garantir precisão e eficiência.

## Pré-requisitos

- Python 3.8 ou superior
- Sistema operacional: Linux, Windows ou macOS
- Utilitários do sistema para processamento de documentos:
  - `antiword` para arquivos DOC
  - `tesseract-ocr` e `tesseract-ocr-por` para OCR em PDFs
  - `poppler-utils` para manipulação de PDFs

### Instalação dos Utilitários por Sistema Operacional

#### Ubuntu/Debian (Linux)
```bash
sudo apt-get update
sudo apt-get install -y antiword tesseract-ocr tesseract-ocr-por poppler-utils
```

#### macOS (usando Homebrew)
```bash
brew install antiword tesseract tesseract-lang poppler
```

#### Windows
1. **Instale Tesseract OCR**:
   - Baixe e instale o executável do [site oficial do Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
   - Ou use Chocolatey: `choco install tesseract`

2. **Instale Poppler**:
   - Use conda: `conda install -c conda-forge poppler`
   - Ou baixe os binários do [site do Poppler](https://poppler.freedesktop.org/).

3. **Antiword**:
   - Baixe o binário para Windows do [site do Antiword](https://www.winfield.demon.nl/) e adicione ao PATH.
   - Nota: Suporte limitado; considere converter DOC para DOCX se possível.

## Instalação

1. **Clone o repositório**:
    ```bash
    git clone https://github.com/Igorbraziel/desafio-tecnico-ceia-ufg.git
    ```

2. **Entre na pasta**:
    ```bash
    cd desafio-tecnico-ceia-ufg
    ```

3. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

4. **Instale as dependências Python**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuração

1. **Configure a chave da API**:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env e configure sua OPENAI_API_KEY
   ```

## Uso

1. **Baixe o dataset**:

```bash
python -m scripts.download_dataset
```

Esse script baixa e extrai o conjunto de dados para o diretório `downloads/`.

2. **Execute a extração de itens**:

```bash
python -m src.main --data-path downloads/
```

O comando processará os arquivos na pasta `downloads/` e gerará os resultados na pasta `results/`.

## Testes

Para executar os testes e validar o sistema:

```bash
# Seleção de Documentos
python -m pytest -v tests/extractor/test_document_selector.py

# Extração de texto de PDFs
python -m pytest -v tests/extractor/test_pdf_extractor.py

# Parser de Item
python -m pytest -v tests/parser/test_item_parser.py

# Parser de Texto dos documentos
python -m pytest -v tests/parser/test_text_parser.py

# Serviço LLM
python -m pytest -v tests/services/test_llm_service.py

# Gerenciador de Arquivos
python -m pytest -v tests/utils/test_file_utils.py

# Testa os resultados obtidos
python -m pytest -s -v tests/results/test_gabarito_amostra.py
```

Certifique-se de que o ambiente virtual esteja ativado antes de executar os testes.

## Estrutura do Projeto

- `src/`: Código-fonte principal
  - `extractor/`: Lógica para extração de texto de diversos formatos de arquivo
  - `parser/`: Processamento e limpeza de texto, isolamento de seções
  - `models/`: Definições de esquemas de dados usando Pydantic
  - `services/`: Integração com serviços externos, incluindo LLM
  - `utils/`: Utilitários para manipulação de arquivos e logging
- `scripts/`: Scripts utilitários
  - `download_dataset.py`: Script para baixar e extrair o dataset
- `tests/`: Testes unitários e de avaliação
- `downloads/`: Diretório com os dados de entrada (ignorados pelo Git)
- `results/`: Diretório com os resultados gerados
- `requirements.txt`: Dependências Python
- `schema_saida.json`: Esquema do formato de saída

## Abordagem Técnica

- **Seleção Inteligente de Documentos**: O `DocumentSelector` prioriza documentos relevantes como editais e termos de referência, ignorando outros para reduzir ruído.
- **Extração de Texto**: Utiliza bibliotecas especializadas como PyMuPDF e pdfplumber para PDFs, python-docx para DOCX, antiword para DOC, pandas para planilhas, e extração recursiva de ZIPs.
- **Isolamento de Seção**: Aplica regex para isolar seções de itens, removendo conteúdo irrelevante antes do processamento pela LLM.
- **Scaffold Mínimo**: Gera referências básicas a partir do campo `itens` do JSON, forçando a LLM a extrair descrições completas.
- **LLM (GPT-5-mini)**: Contexto extenso, permite processamento em lote; fallback com chunking para documentos muito grandes.
- **Robustez**: Tratamento abrangente de erros para arquivos corrompidos, ausentes ou mal formatados; OCR como último recurso.

## Avaliação

O sistema inclui testes automatizados para validação contra gabarito e auditoria estrutural, garantindo qualidade e conformidade com o esquema de saída.

## Limitações

- Não determinismo: como a solução depende do serviço de uma LLM, o resultado final pode ter alterações em diferentes execuções.
- PDFs escaneados dependem de OCR (Tesseract), com precisão variável.
- Documentos com layouts não convencionais podem dificultar o isolamento de seções.
- O scaffold fallback tem qualidade limitada quando não há anexos, dependendo de descrições resumidas no JSON.

## Saída

Os resultados são salvos em `results/resultado.json`, seguindo o formato definido em `schema_saida.json`.
