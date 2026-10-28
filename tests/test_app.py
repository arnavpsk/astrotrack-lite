import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app, load_catalogue

def test_dashboard_loads():
    app.config['TESTING'] = True
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'AstroTrack' in response.data

def test_catalogue_has_67_records_and_six_categories():
    df = load_catalogue()
    assert len(df) == 67
    assert df['category'].nunique() == 6

def test_main_pages_load():
    client = app.test_client()
    for path in ['/explore', '/quiz', '/resources', '/download']:
        assert client.get(path).status_code == 200

def test_invalid_upload_is_handled():
    client = app.test_client()
    response = client.post('/explore', data={'csvfile': ( __import__('io').BytesIO(b'not a csv'), 'data.txt')}, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b'Choose a CSV' in response.data
