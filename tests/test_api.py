import pytest
from unittest.mock import patch, MagicMock
from app.api import app

@pytest.fixture
def client():
    """Creates a test client using Flask’s test framework."""
    app.config["TESTING"] = True  # Enable test mode
    with app.test_client() as client:
        yield client  # Provide the test client

def test_homepage(client):
    """Tests if the homepage loads successfully."""
    response = client.get("/")  # Simulate a GET request
    assert response.status_code == 200  # Check HTTP status
    assert b'Hello from windseeker app - made with flask and love <3' in response.data

valid_windguru_station = {
  "_id": {
    "$oid": "67fb605428481f8596ae2f19"
  },
  "name": "Norway, Hemsedal, OPK Grøndalen",
  "id": 1228,
  "online": True
}

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_main_root_api(client):
    response = client.get('/api')
    assert response.data == b'<p>Hello from windseeker app api - more information inside docs<p>'
    assert response.status_code == 200

def test_main_root(client):
    response = client.get('/')
    assert response.data == b'<p>Hello from windseeker app - made with flask and love <3<p>'
    assert response.status_code == 200

@patch("app.api.db.find_all_windguru_stations")
@patch("app.api.db.connect_to_db")
def test_get_windguru_stations_all(mock_connect, mock_find, client):
    # --- Mocks ---
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_connect.return_value = (mock_client, mock_db)

    # Simulate DB return value
    mock_find.return_value = [
        {"_id": "fakeid1", "id": 1234, "name": "Station One"},
        {"_id": "fakeid2", "id": 5678, "name": "Station Two"},
    ]

    # --- Call the endpoint ---
    response = client.get("/api/windguru/stations")

    # --- Assertions ---
    assert response.status_code == 200
    data = response.get_json()
    assert data["length"] == 2
    assert data["stations"][0]["name"] == "Station One"
    assert data["stations"][1]["id"] == 5678
    mock_connect.assert_called_once()
    mock_find.assert_called_once_with(mock_db)
    mock_client.close.assert_called_once()
