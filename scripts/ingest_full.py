import pandas as pd
import sqlite3
import os
import io

def get_db_connection():
    return sqlite3.connect('f1_championship.db')

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
    db_path = 'f1_championship.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS results')
    cursor.execute('DROP TABLE IF EXISTS drivers')
    cursor.execute('DROP TABLE IF EXISTS teams')
    cursor.execute('DROP TABLE IF EXISTS races')
    cursor.execute('DROP TABLE IF EXISTS scores')
    
    cursor.execute('''
        CREATE TABLE teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE drivers (
            driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_name TEXT UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE races (
            race_id INTEGER PRIMARY KEY AUTOINCREMENT,
            race_name TEXT,
            race_date TEXT,
            race_location TEXT,
            is_sprint TEXT,
            year INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            race_id INTEGER,
            driver_id INTEGER,
            team_id INTEGER,
            driver_start_position INTEGER,
            driver_final_position INTEGER,
            grid_result INTEGER,
            driver_fastest_lap TEXT,
            points INTEGER,
            year INTEGER,
            FOREIGN KEY (race_id) REFERENCES races (race_id),
            FOREIGN KEY (driver_id) REFERENCES drivers (driver_id),
            FOREIGN KEY (team_id) REFERENCES teams (team_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            position INTEGER,
            points INTEGER,
            is_sprint TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print('Database schema initialized.')

def get_or_create_entity(cursor, table, name_col, name_val):
    cursor.execute(f'SELECT {table[:-1]}_id FROM {table} WHERE {name_col} = ?', (name_val,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute(f'INSERT INTO {table} ({name_col}) VALUES (?)', (name_val,))
        return cursor.lastrowid

def ingest_2025(name_map):
    raw_dir = 'files/raw/2025'
    db_path = 'f1_championship.db'
    year = 2025
    
    print('Ingesting 2025 data...')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    drivers_csv = pd.read_csv(os.path.join(raw_dir, 'drivers.csv'))
    races_csv = pd.read_csv(os.path.join(raw_dir, 'races.csv'))
    results_csv = pd.read_csv(os.path.join(raw_dir, 'results.csv'))
    scores_csv = pd.read_csv(os.path.join(raw_dir, 'scores.csv'))
    teams_csv = pd.read_csv(os.path.join(raw_dir, 'teams.csv'))

    # 1. Ingest Teams
    for _, row in teams_csv.iterrows():
        get_or_create_entity(cursor, 'teams', 'team_name', row['team_name'])
        
    # 2. Ingest Drivers
    for _, row in drivers_csv.iterrows():
        norm_name = normalize_name(row['driver_name'], name_map)
        get_or_create_entity(cursor, 'drivers', 'driver_name', norm_name)

    # 3. Ingest Races
    race_map = {}
    for _, row in races_csv.iterrows():
        cursor.execute('INSERT INTO races (race_name, race_date, race_location, is_sprint, year) VALUES (?, ?, ?, ?, ?)', 
                       (row['race_name'], row['race_date'], row['race_location'], str(row['is_sprint']).upper(), year))
        race_map[row['race_id']] = cursor.lastrowid

    # 4. Ingest Scores
    for _, row in scores_csv.iterrows():
        cursor.execute('INSERT INTO scores (position, points, is_sprint) VALUES (?, ?, ?)', 
                       (row['position'], row['points'], str(row['is_sprint']).upper()))

    # 5. Ingest Results
    for _, row in results_csv.iterrows():
        real_race_id = race_map[row['race_id']]
        
        cursor.execute('SELECT is_sprint FROM races WHERE race_id = ?', (real_race_id,))
        is_sprint = cursor.fetchone()[0]
        
        cursor.execute('SELECT points FROM scores WHERE position = ? AND is_sprint = ?', (row['driver_final_position'], is_sprint))
        res = cursor.fetchone()
        points = res[0] if res else 0
        
        # Resolve Driver and Team by name for global IDs
        driver_name = drivers_csv[drivers_csv['driver_id'] == row['driver_id']]['driver_name'].values[0]
        norm_driver_name = normalize_name(driver_name, name_map)
        real_driver_id = get_or_create_entity(cursor, 'drivers', 'driver_name', norm_driver_name)
        
        team_name = teams_csv[teams_csv['team_id'] == row['team_id']]['team_name'].values[0]
        real_team_id = get_or_create_entity(cursor, 'teams', 'team_name', team_name)
        
        cursor.execute('''
            INSERT INTO results (race_id, driver_id, team_id, driver_start_position, driver_final_position, grid_result, driver_fastest_lap, points, year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (real_race_id, real_driver_id, real_team_id, row['driver_start_position'], row['driver_final_position'], row['grid_result'], row['driver_fastest_lap'], points, year))
        
    conn.commit()
    conn.close()
    print('2025 data successfully ingested.')

def ingest_2026(name_map):
    raw_dir = 'files/raw/2026'
    db_path = 'f1_championship.db'
    year = 2026
    
    print('Ingesting 2026 data...')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
        
        cursor.execute('SELECT race_id FROM races WHERE race_name = ? AND race_date = ?', (full_race_name, race_date))
        row = cursor.fetchone()
        if row:
            race_id = row[0]
        else:
            cursor.execute('INSERT INTO races (race_name, race_date, race_location, is_sprint, year) VALUES (?, ?, ?, ?, ?)', 
                           (full_race_name, race_date, gp_name, str(is_sprint).upper(), year))
            race_id = cursor.lastrowid
        
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
                
                real_team_id = get_or_create_entity(cursor, 'teams', 'team_name', equipe)
                real_driver_id = get_or_create_entity(cursor, 'drivers', 'driver_name', norm_piloto)
                
                try:
                    final_pos = int(row.get('Pos.', 0))
                    start_pos = int(row.get('Grid', 0))
                    grid_result = final_pos - start_pos
                except:
                    final_pos, grid_result = 0, 0
                
                cursor.execute('SELECT points FROM scores WHERE position = ? AND is_sprint = ?', (final_pos, str(is_sprint).upper()))
                res = cursor.fetchone()
                points = res[0] if res else 0
                
                cursor.execute('''
                    INSERT INTO results (race_id, driver_id, team_id, driver_start_position, driver_final_position, grid_result, driver_fastest_lap, points, year)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (race_id, real_driver_id, real_team_id, row.get('Grid'), final_pos, grid_result, row.get('Melhor tempo'), points, year))
        
    conn.commit()
    conn.close()
    print('2026 data successfully ingested.')

if __name__ == '__main__':
    name_map = load_name_mappings()
    setup_database()
    ingest_2025(name_map)
    ingest_2026(name_map)

