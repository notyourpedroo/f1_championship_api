import csv
import os
import shutil

def transform_silver_to_gold():
    silver_dir = 'silver'
    gold_dir = 'gold'
    
    if os.path.exists(gold_dir):
        shutil.rmtree(gold_dir)
    os.makedirs(gold_dir)

    # --- Helpers ---
    def read_csv(filename):
        with open(f'{silver_dir}/{filename}', mode='r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def write_csv(filename, data, fieldnames):
        with open(f'{gold_dir}/{filename}', mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    # Load Silver data
    drivers = read_csv('silver_drivers.csv')
    teams = read_csv('silver_teams.csv')
    races = read_csv('silver_races.csv')
    race_results = read_csv('silver_race_results.csv')

    # --- Dimensions ---
    
    # dim_drivers
    gold_dim_drivers = []
    for d in drivers:
        gold_dim_drivers.append({
            'driver_id': d['driver_id'],
            'driver_name': d['driver_name'],
            'current_team_id': d['team_id']
        })
    write_csv('dim_drivers.csv', gold_dim_drivers, ['driver_id', 'driver_name', 'current_team_id'])

    # dim_teams
    write_csv('dim_teams.csv', teams, ['team_id', 'team_name'])

    # dim_races
    write_csv('dim_races.csv', races, ['race_id', 'race_name', 'race_date', 'race_location', 'is_sprint'])

    # --- Fact Table ---
    
    # fact_race_results
    gold_fact_race_results = []
    for rr in race_results:
        start_pos = int(rr['driver_start_position'])
        final_pos = int(rr['driver_final_position'])
        
        gold_fact_race_results.append({
            'race_id': rr['race_id'],
            'driver_id': rr['driver_id'],
            'team_id': rr['team_id'],
            'start_position': start_pos,
            'final_position': final_pos,
            'grid_result': rr['grid_result'],
            'fastest_lap': rr['driver_fastest_lap'],
            'points': rr['points'],
            'position_gain': start_pos - final_pos
        })
    
    write_csv('fact_race_results.csv', gold_fact_race_results, 
              ['race_id', 'driver_id', 'team_id', 'start_position', 'final_position', 'grid_result', 'fastest_lap', 'points', 'position_gain'])

    print("Gold layer transformation completed successfully.")

if __name__ == "__main__":
    transform_silver_to_gold()

