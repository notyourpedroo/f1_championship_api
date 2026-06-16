from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from typing import List, Dict, Any
from database import get_db

app = FastAPI(title='F1 Championship API')

@app.get('/load/{year}/{file_type}')
async def load_data(year: int, file_type: str, db: Session = Depends(get_db)):
    valid_types = {'races', 'drivers', 'results', 'teams', 'scores'}
    if file_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Arquivo '{file_type}' não encontrado.")

    try:
        if file_type == 'scores':
            query = text('SELECT * FROM scores')
            df = pd.DataFrame(db.execute(query).fetchall(), columns=db.execute(query).keys())
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
            raise HTTPException(status_code=404, detail=f"Nenhum dado encontrado para o ano {year} e tipo {file_type}.")

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
