import sys
from os import path
from typing import Dict, Any
import json
from flask import Flask
import pytest

# 将路径添加到 sys.path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from app import create_app


@pytest.fixture()
def app():
    app = create_app("testing")
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


class TestUser:
    def setup_method(self):
        from app.utils import getmd5

        self._email = "123456789@qq.com"
        self._password = getmd5("123456")

    def test_register_on_error(self, client):
        password: str = self._password
        rv = client.post(
            "/user/register", json={"email": self._email, "password": self._password,}
        )

        rv = client.post(
            "/user/register", json={"email": self._email, "password": self._password,}
        )

        assert rv.status_code == 400

    def test_login(self, client):
        password = self._password
        rv = client.post(
            "/user/login", json={"email": self._email, "password": self._password,}
        )
        assert rv.status_code == 200

        response: Dict[str, Any] = json.loads(rv.data)
        print(response, type(response))
        body: Dict[str, Any] = response.get("data")
        assert body.get('user_id') != None
        assert body.get('token') != None
