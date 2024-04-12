from fastapi.testclient import TestClient
import warnings

from main import app

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", module="passlib")

client = TestClient(app)

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
