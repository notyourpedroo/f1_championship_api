from database import engine, SessionLocal
import pandas as pd
import os
import io
from sqlalchemy import text

def load_name_mappings():
    mapping_file = 'files/raw/name_changes/driver_names.csv'
    name_map = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, mode='r', encoding='utf-8') as f:
            # Skip header
            next(f)
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    old_name, new_name = parts
                    name_map[old_name] = new_name
    return name_map

def normalize_name(name, name_map):
    return name_map.get(name, name)

def setup_database():
    with engine.connect() as conn:
        conn.execute(text('DROP TABLE IF EXISTS results'))
        conn.execute(text('DROP TABLE IF EXISTS drivers'))
        conn.execute(text('DROP TABLE IF EXISTS teams'))
        conn.execute(text('DROP TABLE IF EXISTS races'))
        conn.execute(text('DROP TABLE IF EXISTS scores'))
        
        conn.execute(text('CREATE TABLE teams (team_id INTEGER PRIMARY KEY AUTOINCREMENT, team_name TEXT UNIQUE)'))
        conn.execute(text('CREATE TABLE drivers (driver_id INTEGER PRIMARY KEY AUTOINCREMENT, driver_name TEXT UNIQUE)'))
        conn.execute(text('CREATE TABLE races (race_id INTEGER PRIMARY KEY AUTOINCREMENT, race_name TEXT, race_date TEXT, race_location TEXT, is_sprint TEXT, year INTEGER)'))
        
        conn.execute(text('CREATE TABLE results (result_id INTEGER PRIMARY KEY AUTOINCREMENT, race_id INTEGER, driver_id INTEGER, team_id INTEGER, driver_start_position INTEGER, driver_final_position INTEGER, grid_result INTEGER, driver_fastest_lap TEXT, points INTEGER, year INTEGER, FOREIGN KEY (race_id) REFERENCES races (race_id), FOREIGN KEY (driver_id) REFERENCES drivers (driver_id), FOREIGN KEY (team_id) REFERENCES teams (team_id))'))
        
        conn.execute(text('CREATE TABLE scores (score_id INTEGER PRIMARY KEY AUTOINCREMENT, position INTEGER, points INTEGER, is_sprint TEXT)'))
        conn.commit()
        print('Database schema initialized.')

def get_or_create_entity(conn, table, name_col, name_val):
    res = conn.execute(text(f'SELECT {table[:-1]}_id FROM {table} WHERE {name_col} = :name_val'), {'name_val': name_val}).fetchone()
    if res:
        return res[0]
    else:
        res = conn.execute(text(f'INSERT INTO {table} ({name_col}) VALUES (:name_val)'), {'name_val': name_val})
        return res.lastrowid

def ingest_2025(name_map):
    raw_dir = 'files/raw/2025'
    year = 2025
    
    print('Ingesting 2025 data...')
    with engine.connect() as conn:
        drivers_csv = pd.read_csv(os.path.join(raw_dir, 'drivers.csv'))
        races_csv = pd.read_csv(os.path.join(raw_dir, 'races.csv'))
        results_csv = pd.read_csv(os.path.join(raw_dir, 'results.csv'))
        scores_csv = pd.read_csv(os.path.join(raw_dir, 'scores.csv'))
        teams_csv = pd.read_csv(os.path.join(raw_dir, 'teams.csv'))
        
        # 1. Ingest Teams
        for _, row in teams_csv.iterrows():
            get_or_create_entity(conn, 'teams', 'team_name', row['team_name'])
            
        # 2. Ingest Drivers
        for _, row in drivers_csv.iterrows():
            norm_name = normalize_name(row['driver_name'], name_map)
            get_or_create_entity(conn, 'drivers', 'driver_name', norm_name)
        
        # 3. Ingest Races
        race_map = {}
        for _, row in races_csv.iterrows():
            res = conn.execute(text('INSERT INTO races (race_name, race_date, race_location, is_sprint, year) VALUES (:race_name, :race_date, :race_location, :is_sprint, :year)'), 
                                {'race_name': row['race_name'], 'race_date': row['race_date'], 'race_location': row['race_location'], 'is_sprint': str(row['is_sprint']).upper(), 'year': year})
            race_map[row['race_id']] = res.lastrowid
        
        # 4. Ingest Scores
        for _, row in scores_csv.iterrows():
            conn.execute(text('INSERT INTO scores (position, points, is_sprint) VALUES (:position, :points, :is_sprint)'), 
                            {'position': row['position'], 'points': row['points'], 'is_sprint': str(row['is_sprint']).upper()})
        
        # 5. Ingest Results
        for _, row in results_csv.iterrows():
            real_race_id = race_map[row['race_id']]
            
            res_sprint = conn.execute(text('SELECT is_sprint FROM races WHERE race_id = :race_id'), {'race_id': real_race_id}).fetchone()
            is_sprint = res_sprint[0]
            
            res_score = conn.execute(text('SELECT points FROM scores WHERE position = :position AND is_sprint = :is_sprint'), 
                                      {'position': row['driver_final_position'], 'is_sprint': is_sprint}).fetchone()
            points = res_score[0] if res_score else 0
            
            # Use .iloc[0] to get values safely from pandas Series/Arrays
            driver_name = drivers_csv[drivers_csv['driver_id'] == row['driver_id']]['driver_name'].iloc[0]
            norm_driver_name = normalize_name(driver_name, name_map)
            real_driver_id = get_or_create_entity(conn, 'drivers', 'driver_name', norm_driver_name)
            
            team_name = teams_csv[teams_csv['team_id'] == row['team_id']]['team_name'].iloc[0]
            real_team_id = get_or_create_entity(conn, 'teams', 'team_name', team_name)
            
            conn.execute(text('INSERT INTO results (race_id, driver_id, team_id, driver_start_position, driver_final_position, grid_result, driver_fastest_lap, points, year) VALUES (:race_id, :driver_id, :team_id, :driver_start_position, :driver_final_position, :grid_result, :driver_fastest_lap, :points, :year)'), 
                            {'race_id': real_race_id, 'driver_id': real_driver_id, 'team_id': real_team_id, 'driver_start_position': row['driver_start_position'], 'driver_final_position': row['driver_final_position'], 'grid_result': row['grid_result'], 'driver_fastest_lap': row['driver_fastest_lap'], 'points': points, 'year': year})
        
        conn.commit()
        print('2025 data successfully ingested.')
        
def ingest_2026(name_map):
    raw_dir = 'files/raw/2026'
    year = 2026
    
    print('Ingesting 2026 data...')
    with engine.connect() as conn:
        # Sorting: Primary key is date (suffix), Secondary key is Sprint (0) before Race (1)
        files = sorted([f for f in os.listdir(raw_dir) if f.endswith('.csv')], 
                        key=lambda x: (x.split('_')[-1], 0 if 'sprint' in x.lower() else 1))
        
        for filename in files:
            print(f'Processing {filename}...')
            parts = filename.replace('.csv', '').split('_')
            if len(parts) < 3: continue
            gp_name = ' '.join(parts[:-2]).title()
            race_type = parts[-2].lower()
            race_date = parts[-1]
            is_sprint = race_type == 'sprint'
            full_race_name = f'GP de {gp_name}' + (' (SPRINT)' if is_sprint else '')
            
            res = conn.execute(text('SELECT race_id FROM races WHERE race_name = :race_name AND race_date = :race_date'), 
                                    {'race_name': full_race_name, 'race_date': race_date})
            row = res.fetchone()
            if row:
                race_id = row[0]
            else:
                res = conn.execute(text('INSERT INTO races (race_name, race_date, race_location, is_sprint, year) VALUES (:race_name, :race_date, :race_location, :is_sprint, :year)'), 
                                        {'race_name': full_race_name, 'race_date': race_date, 'race_location': gp_name, 'is_sprint': str(is_sprint).upper(), 'year': year})
                race_id = res.lastrowid
            
            with open(os.path.join(raw_dir, filename), mode='r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                section1_lines = []
                for line in lines:
                    stripped = line.strip()
                    if not stripped or all(c == ',' for c in stripped): break
                    section1_lines.append(line)
                
                if not section1_lines: continue
                df = pd.read_csv(io.StringIO(''.join(section1_lines)))
                
                for _, row in df.iterrows():
                    piloto = str(row.get('Piloto', '')).strip()
                    if not piloto or piloto == 'Pessoa': continue
                    norm_piloto = normalize_name(piloto, name_map)
                    equipe = str(row.get('Equipe', '')).strip()
                    
                    real_team_id = get_or_create_entity(conn, 'teams', 'team_name', equipe)
                    real_driver_id = get_or_create_entity(conn, 'drivers', 'driver_name', norm_piloto)
                    
                    try:
                        final_pos = int(row.get('Pos.', 0))
                        start_pos = int(row.get('Grid', 0))
                        grid_result = final_pos - start_pos
                    except:
                        final_pos, grid_result = 0, 0
                    
                    res_score = conn.execute(text('SELECT points FROM scores WHERE position = :position AND is_sprint = :is_sprint'), 
                                             {'position': final_pos, 'is_sprint': str(is_sprint).upper()}).fetchone()
                    points = res_score[0] if res_score else 0
                    
                    conn.execute(text('INSERT INTO results (race_id, driver_id, team_id, driver_start_position, driver_final_position, grid_result, driver_fastest_lap, points, year) VALUES (:race_id, :driver_id, :team_id, :driver_start_position, :driver_final_position, :grid_result, :driver_fastest_lap, :points, :year)'), 
                                    {'race_id': race_id, 'driver_id': real_driver_id, 'team_id': real_team_id, 'driver_start_position': row.get('Grid'), 'driver_final_position': final_pos, 'grid_result': grid_result, 'driver_fastest_lap': row.get('Melhor tempo'), 'points': points, 'year': year})
            
            conn.commit()
            print('2026 data successfully ingested.')

if __name__ == '__main__':
    name_map = load_name_mappings()
    setup_database()
    ingest_2025(name_map)
    ingest_2026(name_map)
