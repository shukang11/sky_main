import pytest
from typing import Optional, Any
from app import create_app
from app.utils import getmd5


DEFAULT_LOGIN_PARAMS = {"email": "123456789@qq.com", "password": getmd5("123456"),}

def get_token(client, login_params) -> str:
    rv = client.post("/user/login", json=login_params)
    return rv.json["data"]["token"]


@pytest.fixture(scope="module")
def app():
    app = create_app("testing")
    yield app


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()
