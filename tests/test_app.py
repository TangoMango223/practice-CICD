"""
Tests for the Flask LLM application
"""
import pytest
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_home_endpoint(client):
    """Test the home page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_chat_endpoint_no_message(client):
    """Test chat endpoint with no message"""
    response = client.post('/chat', json={})
    assert response.status_code == 400
    assert 'error' in response.json