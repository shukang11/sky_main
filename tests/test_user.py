import sys
from os import path
import json
from flask import Flask
import pytest
from .helper import get_token
from app import create_app

# 将路径添加到 sys.path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


@pytest.fixture(scope="module")
def app():
    app = create_app("testing")
    yield app


@pytest.fixture(scope="module")
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

        body = rv.json["data"]
        self._token = body.get("token")
        self._user_id = body.get("user_id")
        assert body.get("user_id") != None
        assert body.get("token") != None

    def test_info(self, client):
        token = get_token(client, email=self._email, password=self._password)
        rv = client.get("/user/info", headers={"token": token})
        assert rv.status_code == 200
        body = rv.json["data"]
        assert body.get("email") == self._email
        assert body.get("account_status") == 1
        assert body.get("user_id") == 1
        assert body.get("nickname") == None

    def test_change_info(self, client):
        token = get_token(client, email=self._email, password=self._password)
        nickname = "nickname"
        sex  = 1
        phone = '13859943743'
        rv = client.post("/user/modify_info", json={"nickname": nickname, "phone": phone, "sex": sex}, headers={"token": token})
        print(rv.json)
        assert rv.status_code == 200
        rv = client.get("/user/info", headers={"token": token})
        body = rv.json["data"]
        print(body)
        assert body.get("email") == self._email
        assert body.get("account_status") == 1
        assert body.get("user_id") == 1
        assert body.get("nickname") == nickname
        assert body.get("sex") == sex
        assert body.get("phone") == phone
