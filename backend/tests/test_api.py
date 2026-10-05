import sys; sys.path.insert(0,'backend')
from fastapi.testclient import TestClient
from app.main import app
def test_public_health_endpoints():
    client=TestClient(app); assert client.get('/health').status_code==200; assert client.get('/ready').status_code in {200,503}
def test_auth_requires_valid_credentials():
    client=TestClient(app); assert client.post('/api/v1/auth/login',json={'email':'nobody@example.com','password':'wrong-password'}).status_code==401
