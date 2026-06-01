import csv
import os

# Paths
silver_path = '/home/pedro/paperclip/PX/project_f1_api/silver'
gold_path = '/home/pedro/paperclip/PX/project_f1_api/gold'

os.makedirs(gold_path, exist_ok=True)

def read_csv(file_name):
    with open(f'{silver_path}/{file_name}', 'r') as f:
        return list(csv.DictReader(f))

def write_csv(file_name, data, fieldnames):
    with open(f'{gold_path}/{file_name}', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Load data
drivers = read_csv('silver_drivers.csv')
races = read_csv('silver_races.csv')
results = read_csv('silver_race_results.csv')
teams = read_csv('silver_teams.csv')

# 1. Dim Driver
dim_driver = [{'driver_id': d['driver_id'], 'driver_name': d['driver_name']} for d in drivers]
write_csv('dim_driver.csv', dim_driver, ['driver_id', 'driver_name'])

# 2. Dim Race
dim_race = [{'race_id': r['race_id'], 'race_name': r['race_name'], 'race_date': r['race_date'], 'race_location': r['race_location'], 'is_sprint': r['is_sprint']} for r in races]
write_csv('dim_race.csv', dim_race, ['race_id', 'race_name', 'race_date', 'race_location', 'is_sprint'])

# 3. Dim Team
dim_team = [{'team_id': t['team_id'], 'team_name': t['team_name']} for t in teams]
write_csv('dim_team.csv', dim_team, ['team_id', 'team_name'])

# 4. Fact Race Results
fact_results = []
for r in results:
    fact_results.append({
        'race_id': r['race_id'],
        'driver_id': r['driver_id'],
        'team_id': r['team_id'],
        'start_position': r['driver_start_position'],
        'final_position': r['driver_final_position'],
        'grid_result': r['grid_result'],
        'fastest_lap': r['driver_fastest_lap'],
        'points': r['points']
    })
write_csv('fact_race_results.csv', fact_results, ['race_id', 'driver_id', 'team_id', 'start_position', 'final_position', 'grid_result', 'fastest_lap', 'points'])

print("Gold layer generated successfully.")
