# F1 Championship API

Uma API REST leve construída com Flask que fornece acesso dinâmico a dados do campeonato de Fórmula 1 armazenados no Google Sheets. Este projeto demonstra como integrar dados de planilhas externas como fonte de dados para um serviço web.

## 🚀 Funcionalidades

A API oferece endpoints para recuperar dados de várias categorias do campeonato. Todos os dados são buscados em tempo real no Google Sheets e retornados no formato JSON.

### Endpoints

| Endpoint | Descrição | Exemplo de Resposta |
| :--- | :--- | :--- |
| `/load/races` | Informações das corridas (Nome, Data, Local) | `[{"race_id": 1, "race_name": "GP da Austrália", "race_date": "2025-03-16", ...}]` |
| `/load/drivers` | Perfis e informações dos pilotos | `[{"driver_id": 1, "team_id": 1, "driver_name": "José", ...}]` |
| `/load/results` | Resultados das corridas e posições | `[{"race_id": 1, "driver_id": 1, "driver_final_position": 6, ...}]` |
| `/load/teams` | Detalhes das equipes e construtores | `[{"team_id": 1, "team_name": "Oracle Red Bull Racing", ...}]` |
| `/load/scores` | Atribuição de pontos por posição | `[{"score_id": 1, "position": 1, "points": 25, ...}]` |

## 🛠️ Instalação e Configuração

### Pré-requisitos

- **Python 3.x**
- **pip** (gerenciador de pacotes do Python)

### Passos de Configuração

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/notyourpedroo/f1_championship_api.git
   cd f1_championship_api
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as Variáveis de Ambiente:**
   Crie um arquivo `.env` no diretório raiz para armazenar os IDs do Google Sheets:
   ```env
   RACES_ID=seu_id_de_arquivo_races
   DRIVERS_ID=seu_id_de_arquivo_drivers
   RESULTS_ID=seu_id_de_arquivo_results
   TEAMS_ID=seu_id_de_arquivo_teams
   SCORES_ID=seu_id_de_arquivo_scores
   ```
   *Nota: Você pode encontrar o ID do arquivo na URL da sua planilha do Google: `docs.google.com/spreadsheets/d/[ID_DO_ARQUIVO]/edit`.*

## 🏃 Executando o Projeto

Inicie o servidor Flask:
```bash
python app.py
```
O servidor estará disponível em `http://127.0.0.1:5000/`.

### Exemplo de Uso
Para obter os dados dos pilotos, basta acessar:
`GET http://127.0.0.1:5000/load/drivers`

## 🤝 Contribuição

Contribuições são bem-vindas! Siga estes passos:
1. Faça um Fork do projeto.
2. Crie sua branch de funcionalidade (`git checkout -b feature/NovaFuncionalidade`).
3. Faça o commit de suas alterações (`git commit -m 'Adiciona NovaFuncionalidade'`).
4. Faça o push para a branch (`git push origin feature/NovaFuncionalidade`).
5. Abra um Pull Request.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.
