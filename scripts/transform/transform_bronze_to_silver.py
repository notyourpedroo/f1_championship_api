import csv
import os
import re

# Paths
BRONZE_DIR_2025 = '/home/pedro/paperclip/PX/project_f1_api/files/bronze/2025'
BRONZE_DIR_2026 = '/home/pedro/paperclip/PX/project_f1_api/files/bronze/2026'
SILVER_DIR = '/home/pedro/paperclip/PX/project_f1_api/files/silver'

FILES_2025 = ['drivers.csv', 'races.csv', 'results.csv', 'scores.csv', 'teams.csv']

def load_silver_mapping(filename, key_col, val_col):
    path = os.path.join(SILVER_DIR, f'silver_{filename}.csv')
    mapping = {}
    if os.path.exists(path):
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mapping[row[val_col]] = row[key_col]
    return mapping

def save_silver_mapping(filename, fieldnames, data):
    path = os.path.join(SILVER_DIR, f'silver_{filename}.csv')
    with open(path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def clean_csv(filename):
    input_path = os.path.join(BRONZE_DIR_2025, filename)
    output_path = os.path.join(SILVER_DIR, f'silver_{filename}')
    
    if not os.path.exists(input_path):
        return []

    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = [f.strip() for f in reader.fieldnames]
        
        rows = []
        for row in reader:
            cleaned_row = {k.strip(): (v.strip() if v else '') for k, v in row.items()}
            rows.append(cleaned_row)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    return rows

def transform_results_2025(results_rows, races_rows, scores_rows):
    race_sprint_map = {r['race_id']: r['is_sprint'].upper() == 'TRUE' for r in races_rows}
    score_map = {}
    for s in scores_rows:
        is_sprint = s['is_sprint'].upper() == 'TRUE'
        score_map[(s['position'], is_sprint)] = s['points']
        
    enriched_results = []
    for res in results_rows:
        race_id = res['race_id']
        final_pos = res['driver_final_position']
        is_sprint = race_sprint_map.get(race_id, False)
        points = score_map.get((final_pos, is_sprint), 0)
        enriched_row = res.copy()
        enriched_row['points'] = points
        enriched_results.append(enriched_row)
        
    if enriched_results:
        fieldnames = list(enriched_results[0].keys())
        output_path = os.path.join(SILVER_DIR, 'silver_race_results.csv')
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched_results)

def process_2026_data():
    print("Processing 2026 data...")
    
    driver_map = {}
    if os.path.exists(os.path.join(SILVER_DIR, 'silver_drivers.csv')):
        with open(os.path.join(SILVER_DIR, 'silver_drivers.csv'), 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if row['driver_name'] != 'Pessoa':
                    driver_map[row['driver_name']] = row['driver_id']
    team_map = load_silver_mapping('teams', 'team_id', 'team_name')
    # Initialize race map with name_date keys
    race_map = {}
    if os.path.exists(os.path.join(SILVER_DIR, 'silver_races.csv')):
        with open(os.path.join(SILVER_DIR, 'silver_races.csv'), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row['race_name']}_{row['race_date']}"
                race_map[key] = row['race_id']
    
    drivers_list = []
    teams_list = []
    races_list = []
    results_list = []

    # Initialize with existing data to maintain IDs
    if os.path.exists(os.path.join(SILVER_DIR, 'silver_drivers.csv')):
        with open(os.path.join(SILVER_DIR, 'silver_drivers.csv'), 'r', encoding='utf-8') as f:
            drivers_list = [row for row in csv.DictReader(f) if row['driver_name'] != 'Pessoa']
    if os.path.exists(os.path.join(SILVER_DIR, 'silver_teams.csv')):
        with open(os.path.join(SILVER_DIR, 'silver_teams.csv'), 'r', encoding='utf-8') as f:
            teams_list = list(csv.DictReader(f))
    if os.path.exists(os.path.join(SILVER_DIR, 'silver_races.csv')):
        with open(os.path.join(SILVER_DIR, 'silver_races.csv'), 'r', encoding='utf-8') as f:
            races_list = list(csv.DictReader(f))
    if os.path.exists(os.path.join(SILVER_DIR, 'silver_race_results.csv')):
        with open(os.path.join(SILVER_DIR, 'silver_race_results.csv'), 'r', encoding='utf-8') as f:
            results_list = [row for row in csv.DictReader(f) if row['driver_id'] in driver_map]

    files = [f for f in os.listdir(BRONZE_DIR_2026) if f.endswith('.csv')]
    
    for filename in files:
        print(f"Processing {filename}...")
        
        # Parse filename: {nome_do_gp}_{tipo_de_corrida}_{data}.csv
        parts = filename.replace('.csv', '').split('_')
        if len(parts) < 3:
            continue
        
        gp_name = " ".join(parts[:-2]).title()
        race_type = parts[-2] # race or sprint
        race_date = parts[-1]
        
        is_sprint = race_type.lower() == 'sprint'
        full_race_name = f"GP de {gp_name}" + (" (SPRINT)" if is_sprint else "")
        
        # Handle race ID
        race_key = f"{full_race_name}_{race_date}"
        if race_key not in race_map:
            race_id = str(len(races_list) + 1)
            race_map[race_key] = race_id
            races_list.append({
                'race_id': race_id,
                'race_name': full_race_name,
                'race_date': race_date,
                'race_location': gp_name,
                'is_sprint': str(is_sprint).upper()
            })
        else:
            race_id = race_map[race_key]
            
        with open(os.path.join(BRONZE_DIR_2026, filename), mode='r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            
            # Extract Section 1 (until first blank line or line with only commas)
            section1_lines = []
            for line in lines:
                stripped = line.strip()
                if not stripped or all(c == ',' for c in stripped):
                    break
                section1_lines.append(line)
            
            if not section1_lines:
                continue
                
            reader = csv.DictReader(section1_lines)
            print(f"Fieldnames for {filename}: {reader.fieldnames}")
            for row in reader:
                piloto = row.get('Piloto', '').strip()
                if not piloto or piloto == 'Pessoa':
                    continue
                equipe = row.get('Equipe', '').strip()
                
                # Handle Team ID
                if equipe not in team_map:
                    team_id = str(len(teams_list) + 1)
                    team_map[equipe] = team_id
                    teams_list.append({'team_id': team_id, 'team_name': equipe})
                else:
                    team_id = team_map[equipe]
                
                # Handle Driver ID
                if piloto not in driver_map:
                    driver_id = str(len(drivers_list) + 1)
                    driver_map[piloto] = driver_id
                    drivers_list.append({'driver_id': driver_id, 'team_id': team_id, 'driver_name': piloto})
                else:
                    driver_id = driver_map[piloto]
                
                # Calculate grid_result
                try:
                    final_pos_str = row.get('Pos.', '0')
                    start_pos_str = row.get('Grid', '0')
                    final_pos = int(final_pos_str) if final_pos_str else 0
                    start_pos = int(start_pos_str) if start_pos_str else 0
                    grid_result = final_pos - start_pos
                except (ValueError, TypeError):
                    final_pos = 0
                    grid_result = 0
                
                results_list.append({
                    'race_id': race_id,
                    'driver_id': driver_id,
                    'team_id': team_id,
                    'driver_start_position': row.get('Grid', '0'),
                    'driver_final_position': row.get('Pos.', '0'),
                    'grid_result': grid_result,
                    'driver_fastest_lap': row.get('Melhor tempo', ''),
                    'points': row.get('Pts.', '0')
                })

    # Save all updated Silver files
    save_silver_mapping('drivers', ['driver_id', 'team_id', 'driver_name'], drivers_list)
    save_silver_mapping('teams', ['team_id', 'team_name'], teams_list)
    save_silver_mapping('races', ['race_id', 'race_name', 'race_date', 'race_location', 'is_sprint'], races_list)
    save_silver_mapping('race_results', ['race_id', 'driver_id', 'team_id', 'driver_start_position', 'driver_final_position', 'grid_result', 'driver_fastest_lap', 'points'], results_list)

def main():
    print("Starting transformation Bronze -> Silver...")
    
    # 1. Clean 2025 data if present
    data = {}
    for f in FILES_2025:
        print(f"Cleaning 2025 {f}...")
        data[f] = clean_csv(f)
        
    # 2. Enrich 2025 results with points
    if 'results.csv' in data and data['results.csv']:
        print("Enriching 2025 results with points...")
        transform_results_2025(data['results.csv'], data['races.csv'], data['scores.csv'])
    
    # 3. Process 2026 data
    process_2026_data()
    
    print("Transformation complete. Files saved in", SILVER_DIR)

if __name__ == '__main__':
    main()
