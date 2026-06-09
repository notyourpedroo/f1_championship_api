from fastapi import FastAPI, HTTPException
import sqlite3
import pandas as pd
from typing import List, Dict, Any

app = FastAPI(title='F1 Championship API')

DB_PATH = 'f1_championship.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get('/load/{year}/{file_type}')
async def load_data(year: int, file_type: str):
    valid_types = {'races', 'drivers', 'results', 'teams', 'scores'}
    if file_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Arquivo '{file_type}' não encontrado.")

    try:
        conn = get_db_connection()
        
        if file_type == 'scores':
            query = 'SELECT * FROM scores'
            df = pd.read_sql_query(query, conn)
        elif file_type == 'teams':
            # Get teams that participated in that year
            query = '''
                SELECT DISTINCT t.team_id, t.team_name, r.year 
                FROM teams t 
                JOIN results r ON t.team_id = r.team_id 
                WHERE r.year = ?
            '''
            df = pd.read_sql_query(query, conn, params=(year,))
        elif file_type == 'drivers':
            # Get drivers and their team for that year
            query = '''
                SELECT DISTINCT d.driver_id, d.driver_name, r.team_id, r.year 
                FROM drivers d 
                JOIN results r ON d.driver_id = r.driver_id 
                WHERE r.year = ?
            '''
            df = pd.read_sql_query(query, conn, params=(year,))
        elif file_type == 'races':
            query = 'SELECT * FROM races WHERE year = ?'
            df = pd.read_sql_query(query, conn, params=(year,))
        elif file_type == 'results':
            query = 'SELECT * FROM results WHERE year = ?'
            df = pd.read_sql_query(query, conn, params=(year,))
            
        conn.close()
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Nenhum dado encontrado para o ano {year} e tipo {file_type}.")

        if file_type == 'races' and 'race_date' in df.columns:
            df['race_date'] = pd.to_datetime(df['race_date']).dt.strftime('%Y-%m-%d')

        return df.to_dict(orient='records')

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)

