import sys
from os import path
from typing import Dict

from flask import Flask
import pytest

# 将路径添加到 sys.path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from app import create_app


@pytest.fixture("module")
def app():
    app = create_app("testing")
    yield app


@pytest.fixture("module")
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
