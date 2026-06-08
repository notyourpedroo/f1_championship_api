
import pytest
import pandas as pd
import os
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_silver_layer_pessoa_filtered():
    """Verify that 'Pessoa' is filtered out of the Silver layer files."""
    silver_files = [
        "files/silver/silver_drivers.csv",
        "files/silver/silver_race_results.csv",
        "files/silver/silver_teams.csv",
        "files/silver/silver_races.csv",
        "files/silver/silver_scores.csv",
        "files/silver/silver_results.csv"
    ]
    
    for file_path in silver_files:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Check all columns for the value 'Pessoa'
            mask = df.apply(lambda row: row.astype(str).str.contains('Pessoa').any(), axis=1)
            assert not mask.any(), f"Pilot 'Pessoa' found in silver file: {file_path}"
        else:
            pytest.fail(f"Silver file not found: {file_path}")

def test_api_routes_2026_pessoa_filtered(client):
    """Verify that API routes for 2026 do not return records for pilot 'Pessoa'."""
    file_types = ["drivers", "results", "scores", "races", "teams"]
    year = "2026"
    
    for file_type in file_types:
        response = client.get(f'/load/{year}/{file_type}')
        assert response.status_code == 200, f"API route /load/{year}/{file_type} failed with status {response.status_code}"
        
        data = response.get_json()
        for record in data:
            # Check all values in the record for 'Pessoa'
            if any('Pessoa' in str(val) for val in record.values()):
                pytest.fail(f"Pilot 'Pessoa' found in API route /load/{year}/{file_type}: {record}")

if __name__ == "__main__":
    pytest.main([__file__])
