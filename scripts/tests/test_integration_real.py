import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_real_load_races(client):
    response = client.get('/load/2025/races')
    assert response.status_code == 200
    assert len(response.get_json()) > 0

def test_real_load_drivers(client):
    response = client.get('/load/2025/drivers')
    assert response.status_code == 200
    assert len(response.get_json()) > 0

def test_real_load_results(client):
    response = client.get('/load/2025/results')
    assert response.status_code == 200
    assert len(response.get_json()) > 0

def test_real_load_teams(client):
    response = client.get('/load/2025/teams')
    assert response.status_code == 200
    assert len(response.get_json()) > 0

def test_real_load_scores(client):
    response = client.get('/load/2025/scores')
    assert response.status_code == 200
    assert len(response.get_json()) > 0

def test_real_load_invalid_year(client):
    response = client.get('/load/2024/races')
    assert response.status_code == 500
    assert 'Arquivo não encontrado' in response.get_json()['error']
