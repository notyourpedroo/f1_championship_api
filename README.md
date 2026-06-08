# F1 Championship API (Modernized)

Uma API REST de alta performance construída com **FastAPI** que fornece acesso a dados do campeonato de Fórmula 1. O projeto utiliza uma arquitetura de processamento de dados moderna, migrando de arquivos CSV locais para um banco de dados **SQLite**, garantindo integridade referencial e continuidade histórica.

## 🚀 Stack Tecnológica

*   **API Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Assíncrono e alta performance).
*   **Processamento de Dados:** [Pandas](https://pandas.pydata.org/).
*   **Banco de Dados:** [SQLite](https://www.sqlite.org/) (Camada Gold).
*   **Servidor ASGI:** [Uvicorn](https://www.uvicorn.org/).
*   **Ambiente:** Python 3.10+ com venv.

## 🛠️ Arquitetura de Dados

O projeto implementa um pipeline de ingestão que transforma dados brutos (`raw`) em um modelo dimensional no SQLite:

1.  **Normalização de Nomes:** Utiliza `files/raw/name_changes/driver_names.csv` para unificar nomes de pilotos entre diferentes anos.
2.  **Entidades Globais:** Pilotos e Equipes são tratados como entidades únicas. Se um piloto corre em 2025 e 2026, ele mantém o mesmo `driver_id`.
3.  **Ordenação Cronológica:** As corridas são processadas e indexadas rigorosamente por data, garantindo que as **Sprints** sempre precedam as **Corridas Principais** no mesmo dia.
4.  **Enriquecimento de Pontos:** A pontuação é calculada dinamicamente cruzando a posição final do piloto com a tabela de regras de pontuação (`scores`).

## 🏃 Execução do Projeto

### 1. Configuração do Ambiente
```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Pipeline de Ingestão
Para processar os dados brutos e gerar o banco de dados `f1_championship.db`:
```bash
python scripts/ingest_full.py
```

### 3. Iniciando a API
```bash
python app.py
```
O servidor estará disponível em `http://127.0.0.1:5000/`.

## 📡 API Endpoints

A API expõe um endpoint dinâmico para recuperação de dados:

**`GET /load/{year}/{file_type}`**

| Parâmetro | Descrição | Exemplo |
| :--- | :--- | :--- |
| `{year}` | Ano dos dados (ex: 2025, 2026) | `2026` |
| `{file_type}` | Categoria de dados suportada | `drivers`, `teams`, `races`, `results`, `scores` |

**Exemplo de Requisição:**
`GET http://127.0.0.1:5000/load/2026/drivers`

---

### 📂 Estrutura de Pastas Essencial
*   `files/raw/`: Dados brutos (CSV).
*   `scripts/`: Scripts de ingestão e processamento.
*   `app.py`: Código fonte da API FastAPI.
*   `f1_championship.db`: Banco de dados SQLite (Gerado após ingestão).

