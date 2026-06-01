import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_real_load_races(client):
    # This should fail because app.py looks for .xlsx but only .csv exists
    response = client.get('/load/races')
    print(f"\nResponse status: {response.status_code}")
    print(f"Response body: {response.get_json()}")
    assert response.status_code == 500
    assert 'Arquivo não encontrado' in response.get_json()['error']
    assert '.xlsx' in response.get_json()['error']

def test_real_load_drivers(client):
    response = client.get('/load/drivers')
    assert response.status_code == 500
    assert 'Arquivo não encontrado' in response.get_json()['error']

def test_real_load_results(client):
    response = client.get('/load/results')
    assert response.status_code == 500
    assert 'Arquivo não encontrado' in response.get_json()['error']

def test_real_load_teams(client):
    response = client.get('/load/teams')
    assert response.status_code == 500
    assert 'Arquivo não encontrado' in response.get_json()['error']

def test_real_load_scores(client):
    response = client.get('/load/scores')
    assert response.status_code == 500
    assert 'Arquivo não encontrado' in response.get_json()['error']
