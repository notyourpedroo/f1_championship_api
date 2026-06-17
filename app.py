"""
Endpoints da API F1 Championship.

Este módulo define os endpoints RESTful para consulta de dados da Fórmula 1.
Utiliza FastAPI com SQLAlchemy ORM para conexão com banco de dados e pandas
para processamento e formatação de dados.

Endpoints Disponíveis:
    GET /load/{year}/{file_type}
        Carrega dados filtrados por ano e tipo de entidade
        
        Parâmetros:
            year (int): Ano da temporada (2025, 2026)
            file_type (str): Tipo de dados - 'races', 'drivers', 'results', 'teams', ou 'scores'
            
        Returns:
            List[Dict]: Lista de registros no formato JSON
            
        Exemplos de Uso:
            >>> import requests
            >>> # Carregar corridas de 2025
            >>> races = requests.get('http://localhost:5000/load/2025/races').json()
            >>> len(races)  # e.g., 24
            
            >>> # Carregar resultados de 2026
            >>> results = requests.get('http://localhost:5000/load/2026/results').json()

Usage:
    # Executar API como servidor
    python app.py
    
    # Testar endpoint
    curl http://localhost:5000/load/2025/races
"""

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from typing import List, Dict, Any
from database import get_db

app = FastAPI(title='F1 Championship API')


@app.get('/load/{year}/{file_type}')
async def load_data(year: int, file_type: str, db: Session = Depends(get_db)):
    """
    Carrega dados filtrados por ano e tipo de entidade.
    
    Endpoint principal da API para consulta de dados da Fórmula 1.
    Retorna registros filtrados por ano e tipo (races, drivers, results, teams, scores).
    Os dados são retornados em formato JSON via pandas DataFrame.
    
    Args:
        year (int): Ano da temporada (ex: 2025, 2026)
        file_type (str): Tipo de entidade a carregar - um dos valores: 
            'races': Corridas
            'drivers': Pilotos  
            'teams': Equipes
            'results': Resultados das corridas
            'scores': Sistema de pontuação
        
        db (Session): Instância de SQLAlchemy Session injetada via Dependency Injection
        
    Returns:
        List[Dict]: Lista de registros no formato JSON com as columnas apropriadas para cada file_type.
                   Exemplo para races: [{'race_id': 1, 'race_name': 'Monaco GP', ...}]
        
    Raises:
        HTTPException (400): Se file_type não for um valor válido ('races', 'drivers', 
                             'results', 'teams', 'scores')
        HTTPException (404): Se nenhum dado for encontrado para o ano e tipo especificados
        
    Example:
        >>> import requests
        >>> # Carregar corridas de 2025
        >>> races = requests.get('http://localhost:5000/load/2025/races').json()
        >>> len(races)
        24
        
        >>> # Carregar resultados de uma temporada
        >>> results = requests.get('http://localhost:5000/load/2026/results').json()
        >>> print(results[0]['driver_final_position'])
        1
    """
    valid_types = {'races', 'drivers', 'results', 'teams', 'scores'}
    if file_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Arquivo '{file_type}' não encontrado."
        )

    try:
        if file_type == 'scores':
            query = text('SELECT * FROM scores WHERE year = :year ORDER BY CASE WHEN is_sprint = \'FALSE\' THEN 0 ELSE 1 END, position')
            df = pd.DataFrame(db.execute(query, {"year": year}).fetchall(), columns=list(db.execute(query, {"year": year}).keys()))
        elif file_type == 'teams':
            query = text('''
                SELECT DISTINCT t.team_id, t.team_name, r.year 
                FROM teams t 
                JOIN results r ON t.team_id = r.team_id 
                WHERE r.year = :year
            ''')
            df = pd.DataFrame(db.execute(query, {"year": year}).fetchall(), columns=db.execute(query, {"year": year}).keys())
        elif file_type == 'drivers':
            query = text('''
                SELECT DISTINCT d.driver_id, d.driver_name, r.team_id, r.year 
                FROM drivers d 
                JOIN results r ON d.driver_id = r.driver_id 
                WHERE r.year = :year
            ''')
            df = pd.DataFrame(db.execute(query, {"year": year}).fetchall(), columns=db.execute(query, {"year": year}).keys())
        elif file_type == 'races':
            query = text('SELECT * FROM races WHERE year = :year')
            df = pd.DataFrame(db.execute(query, {"year": year}).fetchall(), columns=db.execute(query, {"year": year}).keys())
        elif file_type == 'results':
            query = text('SELECT * FROM results WHERE year = :year')
            df = pd.DataFrame(db.execute(query, {"year": year}).fetchall(), columns=db.execute(query, {"year": year}).keys())
            
        if df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"Nenhum dado encontrado para o ano {year} e tipo {file_type}."
            )

        if file_type == 'races' and 'race_date' in df.columns:
            df['race_date'] = pd.to_datetime(df['race_date']).dt.strftime('%Y-%m-%d')

        return df.to_dict(orient='records')

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
