# F1 Championship API

Uma API REST leve construída com Flask que fornece acesso dinâmico a dados do campeonato de Fórmula 1 armazenados em arquivos CSV locais. Este projeto demonstra como servir dados a partir de arquivos estruturados para um serviço web.

## 🚀 Funcionalidades

A API oferece endpoints para recuperar dados de várias categorias do campeonato. Todos os dados são lidos de arquivos CSV locais e retornados no formato JSON.

### Endpoints

| Endpoint | Descrição | Exemplo de Requisição |
| :--- | :--- | :--- |
| `/load/<year>/<file_type>` | Informações de categorias do campeonato para um ano específico | `GET /load/2025/races` |

Para mais detalhes sobre as rotas e os tipos de arquivos suportados, consulte o [Mapeamento de Rotas](docs/routes_mapping.md).

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
   Crie um arquivo `.env` no diretório raiz para definir os arquivos permitidos:
   ```env
   RACES_ID=races
   DRIVERS_ID=drivers
   RESULTS_ID=results
   TEAMS_ID=teams
   SCORES_ID=scores
   ```
   *Nota: Atualmente, a API utiliza esses valores para validar os tipos de arquivos solicitados.*

## 🏃 Executando o Projeto

Inicie o servidor Flask:
```bash
python app.py
```
O servidor estará disponível em `http://127.0.0.1:5000/`.

### 🚀 Ambiente de Produção
Para executar a aplicação em ambiente de produção, recomenda-se o uso do Gunicorn para melhor performance e estabilidade:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
O projeto também inclui um `Procfile` configurado para deploys em plataformas como Heroku.

### Exemplo de Uso
Para obter os dados dos pilotos do ano de 2025, basta acessar:
`GET http://127.0.0.1:5000/load/2025/drivers`

## 🤝 Contribuição

Contribuições são bem-vindas! Siga estes passos:
1. Faça um Fork do projeto.
2. Crie sua branch de funcionalidade (`git checkout -b feature/NovaFuncionalidade`).
3. Faça o commit de suas alterações (`git commit -m 'Adiciona NovaFuncionalidade'`).
4. Faça o push para a branch (`git push origin feature/NovaFuncionalidade`).
5. Abra um Pull Request.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.
