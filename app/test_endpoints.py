from app.main import app # Getting the variable
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_home():
    response = client.get("/") # request.get("/") --> Similar
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']


def test_post_home():
    response = client.post("/") # request.get("/") --> Similar
    assert response.status_code == 200
    assert "application/json" in response.headers['content-type']

