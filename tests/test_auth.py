from secrets import token_hex

import pytest
from async_asgi_testclient import TestClient


@pytest.fixture(scope="function")
async def access_token_fixture(client: TestClient):
    email = f"{token_hex(5)}@example.com"
    username = token_hex(5)
    password = token_hex(5)

    data = {
        "email": email,
        "username": username,
        "is_superuser": False,
        "password": password
    }

    response = await client.post("/registration/", json=data)
    assert response.status_code == 200

    login_params = {
        "username": username,
        "password": password
    }

    login_response = await client.post("/login/", query_string=login_params)
    assert login_response.status_code == 200

    return login_response.json()["tokens"]["access_token"]

class TestAuth:
    
    email = f"{token_hex(5)}@example.com"
    username = token_hex(5)
    password = token_hex(5)
    
    async def test_registration(self, client: TestClient):
        data = {
            "email": self.email,
            "username": self.username,
            "is_superuser": False,
            "password": self.password
        }
        response = await client.post("/registration/", json=data)
        assert response.status_code == 200
        
    async def test_login(self, client: TestClient):
        params = {
            "username": self.username,
            "password": self.password
        }
        
        response = await client.post("/login/", query_string=params)
        assert response.status_code == 200

        
    async def test_create_folder(self, client: TestClient, access_token_fixture):
        # Проверка, что у нас есть access_token от предыдущего теста
        if not access_token_fixture:
            return {"Message": "Access token is required"}
        
        # Подготовка данных для /create_folder      
        token_data = {
            "token": access_token_fixture
            }
        
        folder_data = {
            "folder_name": "test_folder"
        }

        # Отправка запроса на /create_folder
        response = await client.post("/create_folder", query_string=token_data, json=folder_data)

        # Проверка, что запрос прошел успешно
        assert response.status_code == 200
