
# F1 Championship API
Este projeto cria uma API usando Flask para fornecer dados sobre um campeonato de Fórmula 1. Os dados são armazenados em arquivos do Google Sheets e são lidos dinamicamente através de chamadas de rota.

## Funcionalidades
A API oferece 5 rotas para obter dados de diferentes categorias do campeonato:

- `/load/races`: Retorna informações sobre as corridas.
- `/load/drivers`: Retorna informações sobre os pilotos.
- `/load/results`: Retorna os resultados das corridas.
- `/load/teams`: Retorna informações sobre as equipes.
- `/load/scores`: Retorna a pontuação atribuída às posições.

Os dados são recuperados de planilhas do Google Sheets, sendo lidos e disponibilizados no formato JSON.

## Pré-requisitos
Antes de executar o projeto, certifique-se de ter as seguintes dependências instaladas:

- Python 3.x
- pip (gerenciador de pacotes do Python)

Você também precisará dos seguintes pacotes Python:

- Flask
- pandas
- requests
- python-dotenv

Para instalar as dependências, execute o seguinte comando:

```
bash
pip install -r requirements.txt
```
## Arquivo `.env`
O projeto utiliza o arquivo `.env` para armazenar os IDs dos arquivos no Google Sheets. O arquivo `.env` deve estar presente no diretório do projeto com o seguinte conteúdo:
```
RACES_ID=seu_id_de_arquivo_races
DRIVERS_ID=seu_id_de_arquivo_drivers
RESULTS_ID=seu_id_de_arquivo_results
TEAMS_ID=seu_id_de_arquivo_teams
SCORES_ID=seu_id_de_arquivo_scores
```
Substitua os valores acima pelos IDs dos arquivos de cada planilha do Google Sheets.

## Como rodar o projeto
1 - Clone o repositório para sua máquina local:
```
git clone https://seu_repositorio.git
cd f1_championship_api
```
2 - Instale as dependências:
```
pip install -r requirements.txt
```
3 - Crie um arquivo .env no diretório do projeto com os IDs das planilhas (como descrito acima).

4 - Execute o servidor Flask:
```
python app.py
```
5 - O servidor estará disponível em `http://127.0.0.1:5000/`.

## Exemplo de uso
Com o servidor em execução, você pode acessar as rotas para obter os dados em formato JSON:

- Corridas: `GET http://127.0.0.1:5000/load/races`
- Pilotos: `GET http://127.0.0.1:5000/load/drivers`
- Resultados: `GET http://127.0.0.1:5000/load/results`
- Equipes: `GET http://127.0.0.1:5000/load/teams`
- Pontuação: `GET http://127.0.0.1:5000/load/scores`
