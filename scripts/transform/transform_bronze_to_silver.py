import csv
import os

# Paths
BRONZE_DIR = '/home/pedro/paperclip/PX/project_f1_api/files/2025'
SILVER_DIR = '/home/pedro/paperclip/PX/project_f1_api/silver'

FILES = ['drivers.csv', 'races.csv', 'results.csv', 'scores.csv', 'teams.csv']

def clean_csv(filename):
    input_path = os.path.join(BRONZE_DIR, filename)
    output_path = os.path.join(SILVER_DIR, f'silver_{filename}')
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        # Clean fieldnames
        fieldnames = [f.strip() for f in fieldnames]
        
        rows = []
        for row in reader:
            # Clean values and strip whitespace
            cleaned_row = {k.strip(): (v.strip() if v else '') for k, v in row.items()}
            rows.append(cleaned_row)
            
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    return rows

def transform_results(results_rows, races_rows, scores_rows):
    # Create race_id -> is_sprint mapping
    race_sprint_map = {r['race_id']: r['is_sprint'].upper() == 'TRUE' for r in races_rows}
    
    # Create (position, is_sprint) -> points mapping
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
        
        # Create a copy and add points
        enriched_row = res.copy()
        enriched_row['points'] = points
        enriched_results.append(enriched_row)
        
    # Write to silver_race_results.csv
    if enriched_results:
        fieldnames = list(enriched_results[0].keys())
        output_path = os.path.join(SILVER_DIR, 'silver_race_results.csv')
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched_results)

def main():
    print("Starting transformation Bronze -> Silver...")
    
    # 1. Clean all basic files
    data = {}
    for f in FILES:
        print(f"Cleaning {f}...")
        data[f] = clean_csv(f)
        
    # 2. Enrich results with points
    print("Enriching results with points...")
    transform_results(data['results.csv'], data['races.csv'], data['scores.csv'])
    
    print("Transformation complete. Files saved in", SILVER_DIR)

if __name__ == '__main__':
    main()
