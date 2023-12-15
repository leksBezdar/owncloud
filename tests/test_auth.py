from fastapi.testclient import TestClient
from secrets import token_hex

async def test_registration(client: TestClient):
    data = {
        "email": f"{token_hex(5)}@example.com",
        "username": token_hex(5),
        "is_superuser": False,
        "password": token_hex(5)
    }
    response = client.post("/registration", json=data)
    assert response.status_code == 200