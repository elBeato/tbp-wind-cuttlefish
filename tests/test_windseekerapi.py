# -*- coding: utf-8 -*-
from app.api import app
from app import configuration as config
import pytest

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
    assert b"Hello from windseeker app - made with flusk and love <3" in response.data
