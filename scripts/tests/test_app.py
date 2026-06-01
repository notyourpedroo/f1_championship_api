import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from app import app, get_xlsx_from_local

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_xlsx_from_local_file_not_found():
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = False
        df, error = get_xlsx_from_local('non_existent')
        assert df is None
        assert 'Arquivo não encontrado' in error

def test_get_xlsx_from_local_success():
    with patch('os.path.exists') as mock_exists:
        with patch('pandas.read_excel') as mock_read_excel:
            mock_exists.return_value = True
            mock_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
            mock_read_excel.return_value = mock_df
            
            df, error = get_xlsx_from_local('test_file')
            assert df is not None
            assert error is None
            pd.testing.assert_frame_equal(df, mock_df)

def test_get_xlsx_from_local_error():
    with patch('os.path.exists') as mock_exists:
        with patch('pandas.read_excel') as mock_read_excel:
            mock_exists.return_value = True
            mock_read_excel.side_effect = Exception("Read error")
            
            df, error = get_xlsx_from_local('test_file')
            assert df is None
            assert 'Erro ao ler o arquivo XLSX' in error

def test_load_data_invalid_file_type(client):
    response = client.get('/load/invalid_type')
    assert response.status_code == 400
    assert 'não encontrado' in response.get_json()['error']

def test_load_data_success(client):
    mock_df = pd.DataFrame({'id': [1], 'name': ['Test']})
    with patch('app.get_xlsx_from_local') as mock_get_xlsx:
        mock_get_xlsx.return_value = (mock_df, None)
        with patch('app.file_ids', {'drivers': 'some_id'}):
            response = client.get('/load/drivers')
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 1
            assert data[0]['name'] == 'Test'

def test_load_data_internal_error(client):
    with patch('app.get_xlsx_from_local') as mock_get_xlsx:
        mock_get_xlsx.return_value = (None, "Internal error")
        with patch('app.file_ids', {'races': 'some_id'}):
            response = client.get('/load/races')
            assert response.status_code == 500
            assert response.get_json()['error'] == "Internal error"

def test_load_data_races_date_conversion(client):
    # Testing the specific logic for 'races' date conversion
    mock_df = pd.DataFrame({'race_date': ['2025-03-16', '2025-04-10']})
    with patch('app.get_xlsx_from_local') as mock_get_xlsx:
        mock_get_xlsx.return_value = (mock_df, None)
        with patch('app.file_ids', {'races': 'some_id'}):
            response = client.get('/load/races')
            assert response.status_code == 200
            # Flask's jsonify converts datetime to ISO strings
            data = response.get_json()
            assert '16 Mar 2025' in data[0]['race_date']
